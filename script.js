document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('download-btn');
    const comicIdInput = document.getElementById('comic-id');
    const progressSection = document.getElementById('progress-section');
    const progress = document.getElementById('progress');
    const status = document.getElementById('status');
    const resultSection = document.getElementById('result-section');
    const resultMessage = document.getElementById('result-message');
    const openFolderBtn = document.getElementById('open-folder-btn');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');

    downloadBtn.addEventListener('click', function() {
        const comicId = comicIdInput.value.trim();
        
        if (!comicId) {
            showError('请输入漫画ID');
            return;
        }

        // 显示进度区域
        hideAllSections();
        progressSection.style.display = 'block';
        progress.style.width = '0%';
        status.textContent = '正在提交下载请求...';
        
        // 开始下载
        downloadComic(comicId);
    });

    openFolderBtn.addEventListener('click', function() {
        alert('在完整部署环境中，这将打开下载目录');
        // 在实际应用中，这里会调用系统API打开文件夹
    });

    retryBtn.addEventListener('click', function() {
        const comicId = comicIdInput.value.trim();
        if (comicId) {
            // 重新开始下载
            hideAllSections();
            progressSection.style.display = 'block';
            progress.style.width = '0%';
            status.textContent = '正在提交下载请求...';
            downloadComic(comicId);
        }
    });

    function downloadComic(comicId) {
        status.textContent = '正在发送下载请求...';
        progress.style.width = '10%';

        // 发送请求到后端
        fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `comic_id=${encodeURIComponent(comicId)}`
        })
        .then(response => {
            if (response.status === 202) {
                return response.json();
            } else if (response.status >= 400) {
                return response.json().then(data => {
                    throw new Error(data.message || '请求失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'accepted') {
                // 更新进度
                status.textContent = '下载请求已接受，请稍后查看下载结果';
                progress.style.width = '100%';
                
                // 显示结果
                setTimeout(() => {
                    progressSection.style.display = 'none';
                    resultMessage.textContent = data.message + "（由于网络限制，实际下载可能需要一些时间）";
                    resultSection.style.display = 'block';
                }, 1000);
            } else if (data.status === 'success') {
                // 更新进度
                status.textContent = '下载完成!';
                progress.style.width = '100%';
                
                // 显示结果
                setTimeout(() => {
                    progressSection.style.display = 'none';
                    resultMessage.textContent = data.message;
                    resultSection.style.display = 'block';
                }, 500);
            } else {
                throw new Error(data.message || '下载失败');
            }
        })
        .catch(error => {
            showError('下载出错: ' + error.message);
        });
    }

    function showError(message) {
        hideAllSections();
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
    }

    function hideAllSections() {
        progressSection.style.display = 'none';
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
    }
});