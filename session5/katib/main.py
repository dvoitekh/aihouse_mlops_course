import argparse
import logging
import os

import hypertune
import torchvision
from torchvision import transforms
from torchvision.datasets import ImageFolder
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


WORLD_SIZE = int(os.environ.get("WORLD_SIZE", 1))


def train(args, model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            msg = "Train Epoch: {} [{}/{} ({:.0f}%)]\ttrain_loss={:.4f}".format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item() / len(data))
            logging.info(msg)


def val(args, model, device, val_loader, criterion, epoch, hpt):
    model.eval()
    val_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in val_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            val_loss += criterion(output, target).item()  # sum up batch loss
            pred = output.max(1, keepdim=True)[1]  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    val_loss /= len(val_loader.dataset)
    val_accuracy = float(correct) / len(val_loader.dataset)

    msg = "Val Epoch: {}\tval_loss={:.4f}".format(epoch, val_loss)
    logging.info(msg)

    if args.logger == "hypertune":
        hpt.report_hyperparameter_tuning_metric(
            hyperparameter_metric_tag='loss',
            metric_value=val_loss,
            global_step=epoch)
        hpt.report_hyperparameter_tuning_metric(
            hyperparameter_metric_tag='accuracy',
            metric_value=val_accuracy,
            global_step=epoch)


def should_distribute():
    return dist.is_available() and WORLD_SIZE > 1


def is_distributed():
    return dist.is_available() and dist.is_initialized()


def generate_preprocessing(val=False):
    custom_steps = [transforms.Resize(256), transforms.CenterCrop(224)] if val else [transforms.RandomResizedCrop(224), transforms.RandomHorizontalFlip()]
    return transforms.Compose([
        *custom_steps,
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


def main():
    # Training settings
    parser = argparse.ArgumentParser(description="PyTorch MNIST Example")
    parser.add_argument("--batch-size", type=int, default=8, metavar="N",
                        help="input batch size for training (default: 8)")
    parser.add_argument("--val-batch-size", type=int, default=16, metavar="N",
                        help="input batch size for testing (default: 16)")
    parser.add_argument("--epochs", type=int, default=10, metavar="N",
                        help="number of epochs to train (default: 10)")
    parser.add_argument("--lr", type=float, default=0.01, metavar="LR",
                        help="learning rate (default: 0.01)")
    parser.add_argument("--momentum", type=float, default=0.5, metavar="M",
                        help="SGD momentum (default: 0.5)")
    parser.add_argument("--no-cuda", action="store_true", default=False,
                        help="disables CUDA training")
    parser.add_argument("--seed", type=int, default=1, metavar="S",
                        help="random seed (default: 1)")
    parser.add_argument("--log-interval", type=int, default=10, metavar="N",
                        help="how many batches to wait before logging training status")
    parser.add_argument("--log-path", type=str, default="",
                        help="Path to save logs. Print to StdOut if log-path is not set")
    parser.add_argument("--save-model", action="store_true", default=False,
                        help="For Saving the current Model")
    parser.add_argument("--logger", type=str, choices=["standard", "hypertune"],
                        help="Logger", default="standard")

    if dist.is_available():
        parser.add_argument("--backend", type=str, help="Distributed backend",
                            choices=[dist.Backend.GLOO, dist.Backend.NCCL, dist.Backend.MPI],
                            default=dist.Backend.GLOO)
    args = parser.parse_args()

    # Use this format (%Y-%m-%dT%H:%M:%SZ) to record timestamp of the metrics.
    # If log_path is empty print log to StdOut, otherwise print log to the file.
    if args.log_path == "" or args.logger == "hypertune":
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
            level=logging.DEBUG)
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
            level=logging.DEBUG,
            filename=args.log_path)

    if args.logger == "hypertune" and args.log_path != "":
        os.environ['CLOUD_ML_HP_METRIC_FILE'] = args.log_path

    # For JSON logging
    hpt = hypertune.HyperTune()

    use_cuda = not args.no_cuda and torch.cuda.is_available()
    if use_cuda:
        print("Using CUDA")

    torch.manual_seed(args.seed)

    device = torch.device("cuda" if use_cuda else "cpu")

    if should_distribute():
        print("Using distributed PyTorch with {} backend".format(args.backend))
        dist.init_process_group(backend=args.backend)

    kwargs = {"num_workers": 1, "pin_memory": True} if use_cuda else {}

    train_loader = torch.utils.data.DataLoader(
        ImageFolder('images/train', transform=generate_preprocessing()),
        batch_size=args.batch_size, shuffle=True, **kwargs)

    val_loader = torch.utils.data.DataLoader(
        ImageFolder('images/validation', transform=generate_preprocessing(val=True)),
        batch_size=args.val_batch_size, shuffle=False, **kwargs)

    model = torchvision.models.mobilenet_v2(pretrained=True).to(device)

    if is_distributed():
        Distributor = nn.parallel.DistributedDataParallel if use_cuda \
            else nn.parallel.DistributedDataParallelCPU
        model = Distributor(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)

    for epoch in range(1, args.epochs + 1):
        train(args, model, device, train_loader, optimizer, criterion, epoch)
        val(args, model, device, val_loader, criterion, epoch, hpt)

    if (args.save_model):
        torch.save(model.state_dict(), "facial_emotions_cnn.pt")


if __name__ == "__main__":
    main()
