
const dropArea = document.querySelector('.drop-section');
const listSection = document.querySelector('.list-section');
const listContainer = document.querySelector('.list');
const fileSelector = document.querySelector('.file-selector');
const fileSelectorInput = document.querySelector('.file-selector-input');

fileSelector.onclick = () => fileSelectorInput.click();
fileSelectorInput.onchange = () => {
    [...fileSelectorInput.files].forEach((file) => {
        if (typeValidation(file.type)) {
            uploadFile(file);
        }
    });
};

function typeValidation(type) {
    var splitType = type.split('/')[0];
    return type === 'application/pdf' || splitType === 'image' || splitType === 'video';
}

dropArea.ondragover = (e) => {
    e.preventDefault();
    [...e.dataTransfer.items].forEach((item) => {
        if (typeValidation(item.type)) {
            dropArea.classList.add('drag-over-effect');
        }
    });
};

dropArea.ondragleave = () => {
    dropArea.classList.remove('drag-over-effect');
};

dropArea.ondrop = (e) => {
    e.preventDefault();
    dropArea.classList.remove('drag-over-effect');
    if (e.dataTransfer.items) {
        [...e.dataTransfer.items].forEach((item) => {
            if (item.kind === 'file') {
                const file = item.getAsFile();
                if (typeValidation(file.type)) {
                    uploadFile(file);
                }
            }
        });
    } else {
        [...e.dataTransfer.files].forEach((file) => {
            if (typeValidation(file.type)) {
                uploadFile(file);
            }
        });
    }
};

function uploadFile(file) {
    listSection.style.display = 'block';
    var li = document.createElement('li');
    li.classList.add('in-prog');

    const fileId = Date.now();
    li.innerHTML = `
        <div class="col">
            <img src="icons/${iconSelector(file.type)}" alt="">
        </div>
        <div class="col">
            <div class="file-name">
                <div class="name">${file.name}</div>
                <span>0%</span>
            </div>
            <div class="file-progress">
                <span></span>
            </div>
            <div class="file-size">${(file.size / (1024 * 1024)).toFixed(2)} MB</div>
        </div>
        <div class="col">
            <svg xmlns="http://www.w3.org/2000/svg" class="cross" height="20" width="20">
                <path d="m5.979 14.917-.854-.896 4-4.021-4-4.062.854-.896 4.042 4.062 4-4.062.854.896-4 4.062 4 4.021-.854.896-4-4.063Z"/>
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" class="tick" height="20" width="20">
                <path d="m8.229 14.438-3.896-3.917 1.438-1.438 2.458 2.459 6-6L15.667 7Z"/>
            </svg>
        </div>
    `;

    listContainer.prepend(li);

    const fileData = {
        id: fileId,
        name: file.name,
        type: file.type,
        size: file.size,
        progress: 0,
        completed: false,
    };

    localStorage.setItem(`file_${fileId}`, JSON.stringify(fileData));

    setTimeout(() => {
        fileData.progress = 100;
        fileData.completed = true;
        localStorage.setItem(`file_${fileId}`, JSON.stringify(fileData));

        li.classList.add('complete');
        li.classList.remove('in-prog');
    }, 2000);

    li.querySelector('.cross').onclick = () => {
        localStorage.removeItem(`file_${fileId}`);
        li.remove();
    };

}



function iconSelector(type) {
    var splitType = (type.split('/')[0] === 'application') ? type.split('/')[1] : type.split('/')[0];
    return splitType + '.png';
}

// Load existing files from local storage
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.startsWith('file_')) {
        const fileData = JSON.parse(localStorage.getItem(key));
        if (fileData.completed) {
            const li = document.createElement('li');
            li.classList.add('complete');
            li.innerHTML = `
                <div class="col">
                    <img src="icons/${iconSelector(fileData.type)}" alt="">
                </div>
                <div class="col">
                    <div class="file-name">
                        <div class="name">${fileData.name}</div>
                        <span>100%</span>
                    </div>
                    <div class="file-progress">
                        <span style="width: 100%;"></span>
                    </div>
                    <div class="file-size">${(fileData.size / (1024 * 1024)).toFixed(2)} MB</div>
                </div>
                <div class="col">
                    <svg xmlns="http://www.w3.org/2000/svg" class="cross" height="20" width="20">
                        <path d="m5.979 14.917-.854-.896 4-4.021-4-4.062.854-.896 4.042 4.062 4-4.062.854.896-4 4.062 4 4.021-.854.896-4-4.063Z"/>
                    </svg>
                </div>
            `;

            listContainer.appendChild(li);

            li.querySelector('.cross').onclick = () => {
                localStorage.removeItem(key);
                li.remove();
            };
            
           
        }
    }
}
