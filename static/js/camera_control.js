// $(document).ready(function () {
//     let video = document.getElementById('camera-stream-left');
//     let photos = document.getElementById('capture');
//     let stream = null;
//     var socket = io.connect('http://' + document.domain + ':' + location.port);
//     var videoCanvas = document.getElementById('camera-stream-right');
//     var videoCanvasContext = videoCanvas.getContext('2d');
//     var capturedImages = [];
//     // 开启摄像头
//     $('#start').click(function () {
//         if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
//             navigator.mediaDevices.getUserMedia({video: true}).then(function (localMediaStream) {
//                 video.srcObject = localMediaStream;
//                 stream = localMediaStream;
//                 video.play();
//                 sendFrame();
//             }).catch(function (err) {
//                 console.log("An error occurred: " + err);
//             });
//         }
//
//     });
//
//     function sendFrame() {
//         var canvas = document.createElement('canvas');
//         canvas.width = video.videoWidth;
//         canvas.height = video.videoHeight;
//         var ctx = canvas.getContext('2d');
//         ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
//         var data = canvas.toDataURL('image/jpeg', 0.7);
//         if (data != 'data:,'){
//             socket.emit('frame', data.split(',')[1]);
//         }
//         setTimeout(sendFrame, 100); // Send frames every 100ms
//     }
//
//     socket.on('response', function (data) {
//         var img = new Image();
//         img.onload = function () {
//             videoCanvasContext.clearRect(0, 0, videoCanvas.width, videoCanvas.height);
//             videoCanvasContext.drawImage(img, 0, 0, videoCanvas.width, videoCanvas.height);
//             drawFaces(data.property);
//         };
//         img.src = 'data:image/jpeg;base64,' + data.data;
//         document.getElementById('face-info').innerText = JSON.stringify(data['property'])
//     });
//
//     function drawFaces(data) {
//         data.forEach(face => {
//             var scaleX = videoCanvas.width / video.videoWidth;
//             var scaleY = videoCanvas.height / video.videoHeight;
//             var x = face.x * scaleX;
//             var y = face.y * scaleY;
//             var w = face.w * scaleX;
//             var h = face.h * scaleY;
//
//             videoCanvasContext.beginPath();
//             videoCanvasContext.rect(x, y, w, h);
//             videoCanvasContext.lineWidth = 2;
//             videoCanvasContext.strokeStyle = 'red';
//             videoCanvasContext.stroke();
//             videoCanvasContext.fillStyle = 'red';
//             videoCanvasContext.fillText(face.name, x, y - 10);
//         });
//     }
//
//
//     $('#stop').click(function () {
//         if (stream) {
//             stream.getTracks().forEach(track => track.stop());
//         }
//     });
//
//     function displayImages() {
//         $('#photos').empty();
//         capturedImages.forEach(function (imageData, index) {
//             var imgElement = $('<img>').attr('src', imageData).css({width: '100px', height: 'auto'});
//             var deleteButton = $('<button class="delete">删除</button>').click(function () {
//                 capturedImages.splice(index, 1);
//                 displayImages();
//             });
//             $('#photos').append($('<div class="photo"></div>').append(imgElement).append(deleteButton));
//         });
//     }
//
//     $('#capture').click(function () {
//         var canvas = document.createElement('canvas');
//         canvas.width = video.videoWidth;
//         canvas.height = video.videoHeight;
//         canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//         let dataURL = canvas.toDataURL("image/png");
//
//         capturedImages.push(dataURL);
//         displayImages();
//     });
//
//     $('#clearAll').click(function () {
//         capturedImages.splice(0, capturedImages.length)
//         $('#photos').empty();
//     });
//
//     $('#upload').click(function () {
//         var folderName = $('#folderName').val();
//         if (!folderName) {
//             alert('请输入名称！');
//             return;
//         }
//
//         var formData = new FormData();
//         formData.append('folderName', folderName);
//         console.log(formData.get('folderName'))
//
//         capturedImages.forEach(function(imageData, index) {
//         formData.append('images', imageData);
//     });
//
//         $.ajax({
//             url: '/upload_images',
//             type: 'POST',
//             data: formData,
//             processData: false,
//             contentType: false,
//             success: function (response) {
//                 console.log('上传成功:', response);
//                 alert(response.message)
//             },
//             error: function (error) {
//                 console.error('上传失败:', error);
//             }
//         });
//     });
//
//     $('#training').click(function () {
//          layer.load(0, {shade: false});
//         $.ajax({
//             url: '/training',
//             type: 'GET',
//             processData: false,
//             contentType: false,
//             success: function (response) {
//                 alert(response)
//             },
//             error: function (error) {
//                 console.error('上传失败:', error);
//             }
//         });
//      });
// });
$(document).ready(function () {
    let video = document.getElementById('camera-stream-left');
    let photos = document.getElementById('capture');
    let stream = null;
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var videoCanvas = document.getElementById('camera-stream-right');
    var videoCanvasContext = videoCanvas.getContext('2d');
    var capturedImages = [];

    $('#start').click(function () {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({video: true}).then(function (localMediaStream) {
                video.srcObject = localMediaStream;
                stream = localMediaStream;
                video.play();
                sendFrame();
            }).catch(function (err) {
                console.log("An error occurred: " + err);
            });
        }
    });

    function sendFrame() {
        var canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        var data = canvas.toDataURL('image/jpeg', 0.7);
        if (data != 'data:,'){
            socket.emit('frame', data.split(',')[1]);
        }
        setTimeout(sendFrame, 100); // Send frames every 100ms
    }

    socket.on('response', function (data) {
        var img = new Image();
        img.onload = function () {
            videoCanvasContext.clearRect(0, 0, videoCanvas.width, videoCanvas.height);
            videoCanvasContext.drawImage(img, 0, 0, videoCanvas.width, videoCanvas.height);
            drawFaces(data.property);
        };
        img.src = 'data:image/jpeg;base64,' + data.data;
        displayFaceInfo(data.property);
    });

    function drawFaces(data) {
        data.forEach(face => {
            var scaleX = videoCanvas.width / video.videoWidth;
            var scaleY = videoCanvas.height / video.videoHeight;
            var x = face.x * scaleX;
            var y = face.y * scaleY;
            var w = face.w * scaleX;
            var h = face.h * scaleY;

            videoCanvasContext.beginPath();
            videoCanvasContext.rect(x, y, w, h);
            videoCanvasContext.lineWidth = 2;
            videoCanvasContext.strokeStyle = 'red';
            videoCanvasContext.stroke();
            videoCanvasContext.fillStyle = 'red';
            videoCanvasContext.fillText(`Age: ${face.age}`, x, y - 30);
            videoCanvasContext.fillText(`Gender: ${face.gender}`, x, y - 20);
            videoCanvasContext.fillText(`Emotion: ${face.emotion}`, x, y - 10);
        });
    }

    function displayFaceInfo(data) {
        var faceInfo = document.getElementById('face-info');
        faceInfo.innerHTML = '';
        data.forEach((face, index) => {
            faceInfo.innerHTML += `Face ${index + 1}: Age: ${face.age}, Gender: ${face.gender}, Emotion: ${face.emotion}<br>`;
        });
    }

    $('#stop').click(function () {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    function displayImages() {
        $('#photos').empty();
        capturedImages.forEach(function (imageData, index) {
            var imgElement = $('<img>').attr('src', imageData).css({width: '100px', height: 'auto'});
            var deleteButton = $('<button class="delete">删除</button>').click(function () {
                capturedImages.splice(index, 1);
                displayImages();
            });
            $('#photos').append($('<div class="photo"></div>').append(imgElement).append(deleteButton));
        });
    }

    $('#capture').click(function () {
        var canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        let dataURL = canvas.toDataURL("image/png");

        capturedImages.push(dataURL);
        displayImages();
    });

    $('#clearAll').click(function () {
        capturedImages.splice(0, capturedImages.length)
        $('#photos').empty();
    });

    $('#upload').click(function () {
        var folderName = $('#folderName').val();
        if (!folderName) {
            alert('请输入名称！');
            return;
        }

        var formData = new FormData();
        formData.append('folderName', folderName);
        console.log(formData.get('folderName'))

        capturedImages.forEach(function(imageData, index) {
        formData.append('images', imageData);
    });

        $.ajax({
            url: '/upload_images',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                console.log('上传成功:', response);
                alert(response.message)
            },
            error: function (error) {
                console.error('上传失败:', error);
            }
        });
    });

    $('#training').click(function () {
         layer.load(0, {shade: false});
        $.ajax({
            url: '/training',
            type: 'GET',
            processData: false,
            contentType: false,
            success: function (response) {
                alert(response)
            },
            error: function (error) {
                console.error('上传失败:', error);
            }
        });
    });
});
