## On-device ML tutorial

NOTE: this tutorial is recommended to be launched on your local machine so you can build and run mobile and browser apps with the model.

## Convert the PyTorch model to portable formats

1. Install requirements for models conversion script:

```bash
pip install -r requirements.txt
```

2. Run the script to convert pretrained Imagenet MobileNetV2 model from PyTorch to major portable ML formats (CoreML, TFLite, TorchMobile, ONNX)

```bash
python convert.py
```

3. After it's done, you'll see checkpoints in the [models](./models) directory

4. <b>Additional task</b>. In the end of the script add some code to evaluate the quality of conversion to different formats as suggested in comments. It's up to you to select metrics and assertions to perform.


## Run CoreML model in the iOS/MacOS app

1. On your Mac, open Finder and navigate to [coreml](./coreml) directory

2. Open `Imagenet.xcodeproj` so it will launch your Xcode

3. Change the build target at the top of the window to `My Mac (Catalyst)` and run the app

## Run TF.js with TFLite model

1. From the [sessions9](./sessions9) directory run the file server:

```
python -m http.server 3000
```

2. Navigate to http://localhost:3000/tfjs/ in your browser and test out the classifier on the camera stream



