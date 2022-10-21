import http from 'k6/http';

export default function () {
    const url = 'http://localhost:5000/api/v1/predict';
    const payload = JSON.stringify({
        prompts: ['i love you to the moon and back']
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    http.post(url, payload, params);
}
