const video = document.getElementById("video");
const currentURL = window.location.href;
console.log(currentURL+"0000");
Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri("/static/models"),
  faceapi.nets.faceLandmark68Net.loadFromUri("/static/models"),
]).then(startWebcam);

function startWebcam() {
  navigator.mediaDevices
    .getUserMedia({
      video: true,
      audio: false,
    })
    .then((stream) => {
      video.srcObject = stream;
    })
    .catch((error) => {
      console.error('Không thể khởi động nguồn video:', error);
      alert('Ứng dụng không thể truy cập vào camera. Vui lòng kiểm tra quyền truy cập của bạn và thử lại.');
    });
}
startWebcam()
video.addEventListener("play", () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  document.body.append(canvas);
  faceapi.matchDimensions(canvas, { height: video.height, width: video.width });

  setInterval(async () => {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks();

    const resizedDetections = faceapi.resizeResults(detections, {
      height: video.height,
      width: video.width,
    });
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    canvas.style.position = 'absolute'; // Đảm bảo có position để sử dụng z-index
    canvas.style.top = '50px';
    canvas.style.zIndex = '999'; // Giá trị z-index có thể được điều chỉnh tùy theo nhu cầu
    faceapi.draw.drawDetections(canvas, resizedDetections);

    console.log(detections);
  }, 100);
});
function stopVideo() {
  const video = document.getElementById('video');
  video.pause();
}
function reload() {
  window.location.reload()
}
function captureAndSubmit() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  // Chuyển đổi hình ảnh từ canvas thành base64
  const imageData = canvas.toDataURL('image/jpeg');

  // Lấy giá trị của username từ input
  const username = document.querySelector('input[name="user_name"]').value;

  // Tạo formData chứa hình ảnh và username để gửi lên server
  const formData = new FormData();
  formData.append('image', imageData);
  formData.append('username', username);
  // Gửi dữ liệu lên server
  fetch('/face_login', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (response.ok) {
      // Xử lý kết quả từ server nếu cần
      console.log('Image submitted successfully');
    } else {
      console.error('Failed to submit image');
    }
  })
  .catch(error => {
    console.error('Error sending image to server:', error);
  });
}

document.getElementById('login-button').addEventListener('click', (event) => {
  event.preventDefault(); // Ngăn chặn hành vi mặc định của form
  captureAndSubmit(); // Gọi hàm để gửi dữ liệu
  stopVideo()
});