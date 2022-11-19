async function loadLabels() {
    let response = await fetch("https://raw.githubusercontent.com/dvoitekh/coreml_workshop/master/Imagenet/labels.csv");
    let text = await response.text();
    return text.split('\n').map(x => x.trim()).filter(x => x.length > 0);
}

function getUserMediaSupported() {
    return !!(navigator.mediaDevices &&
        navigator.mediaDevices.getUserMedia);
}


(async () => {
    const tfliteModel = await tflite.loadTFLiteModel('../models/Model.tflite');
    const labels = await loadLabels();

    const video = document.getElementById('webcam');
    const demosSection = document.getElementById('demos');
    const enableWebcamButton = document.getElementById('webcamButton');
    const captureWebcamButton = document.getElementById('captureButton');
    const predictions = document.getElementById('predictions');
    demosSection.classList.remove('invisible');

    if (getUserMediaSupported()) {
        enableWebcamButton.addEventListener('click', enableCam);
    } else {
        console.warn('getUserMedia() is not supported by your browser');
    }

    // Enable the live webcam view and start classification.
    function enableCam(event) {
        // Hide the button once clicked.
        event.target.classList.add('removed');

        // getUsermedia parameters to force video but not audio.
        const constraints = {
            video: true
        };

        // Activate the webcam stream.
        navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
            video.srcObject = stream;
        });
    }

    captureWebcamButton.addEventListener("click", async () => {
        let camera = await tf.data.webcam(video);
        let image = await camera.capture();
        tf.tidy(() => {
            // let img = tf.browser.fromPixels(document.querySelector('img'));
            let img = image;
            img = tf.image.resizeBilinear(img, [224, 224])
            img = tf.div(img, 255);
            img = tf.transpose(img, [2, 0, 1])
            // Normalize (might also do resize here if necessary).
            const mean = tf.expandDims(tf.expandDims(tf.tensor([0.485, 0.456, 0.406]), 1), 1)
            const std = tf.expandDims(tf.expandDims(tf.tensor([0.229, 0.224, 0.225]), 1), 1)
            const input = tf.expandDims(tf.div(tf.sub(img, mean), std), 0)
            // Run the inference.
            let outputTensor = tfliteModel.predict(input);
            let softmax = tf.softmax(outputTensor).dataSync();
            const { _, indices } = tf.topk(outputTensor, 5);
            let newPredictions = [];
            indices.dataSync().forEach((x, i) => {
                const p = document.createElement('p');
                p.id = "prediction-" + i.toString();
                p.innerHTML += labels[x] + ", " + softmax[x].toString();
                newPredictions.push(p);
            });
            predictions.replaceChildren(...newPredictions);
        });
    });
})().catch(e => {
    console.log(e)
});
