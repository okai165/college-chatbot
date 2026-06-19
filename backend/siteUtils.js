export function getNotices(sdepttId) {
    $.ajax({
        url: './src/fetchnotices.php',
        type: 'get',
        data: { null: null },
        dataType: 'json',
        beforeSend: function () {
            showLoaderIcons(sdepttId);
        },
        complete: function (sdepttId) {
            hideLoaderIcons(sdepttId);
        },
        success: function (response) {
            if (response['noticeData'] != "") {
                populateComponents(response, sdepttId);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            alert("Oops! Something went wrong while fetching  Notice Data");
        }

    });
}

export function getDepartmentLeadImage(sdepttId) {

    // let sdepttId = $("#" + sdepttId);

    $.ajax({
        url: './src/fetchDepartLeadImgGromGallery.php',
        type: 'post',
        data: { depttId: sdepttId },
        dataType: 'json',
        beforeSend: function () {
            //    showLoaderIcons();              
        },
        complete: function () {
            // hideLoaderIcons();
        },
        success: function (response) {
            if (response['galleryData'] != "") {
                let bannerImage = (response['galleryData'][0]['leadFileName']);
                $("#deptSliderImage").attr("src", './images/' + bannerImage);
            }
            else {
                document.getElementById('galleryMainCont').innerHTML = "";
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            alert("Oops! Something went wrong while fetching Gallery Data");
        }

    });
}





export function getGalleyImages(depttId, eventId) {

    $.ajax({
        url: './src/fetchGalleryImagesByParms.php',
        type: 'get',
        data: { depttId: depttId },
        dataType: 'json',
        beforeSend: function () {
            //    showLoaderIcons();              
        },
        complete: function () {
            // hideLoaderIcons();
        },
        success: function (response) {
            if (response['galleryData'] != "") {

                populateGalleryComponent(response, depttId, eventId);
            }
            else {
                document.getElementById('galleryMainCont').innerHTML = "";
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            alert("Oops! Something went wrong while fetching Gallery Data");
        }

    });
}


function populateGalleryComponent(galleryData, sdepttId, seventId) {

    let galleryEle = `<div id="galleryMain" class="owl-carousel owl-theme">`;
    galleryData = galleryData['galleryData'];

    if (sdepttId == null && seventId == null)
        document.getElementById("galleryCaption").innerHTML = "Through the Lens";
    else if (sdepttId != null && seventId == null)
        document.getElementById("galleryCaption").innerHTML = "In Pictures";
    else if (sdepttId == null && seventId != null)
        document.getElementById("galleryCaptionCont").innerHTML = "";

    galleryData.forEach((event) => {

        const eventShowOnHome = event['eventShowOnHome'];
        const imgShowOnHome = event['imgShowOnHome'];
        const thumbNail = "./images/" + event['thumbNail'];
        const leadFileName = "./images/" + event['leadFileName'];
        const parenrDepttId = event['deptt_id'];
        const eventId = event['event_Id'];

        let eleCur = `<div class="item">
                                    <a href="${leadFileName}" data-lightbox="gallery" data-title="">
                                    <img src="${thumbNail}" alt="Image ">
                                    <div class="stretch-icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="currentColor" class="bi bi-arrows-angle-expand" viewBox="0 0 16 16">
                                    <path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707m4.344-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707"/>
                                    </svg>
                                    </div>
                                    </a>
                                    </div>`;


        if (eventShowOnHome == 1 && sdepttId == null && seventId == null)
            galleryEle += eleCur;
        else if (sdepttId == parenrDepttId)
            galleryEle += eleCur;
        else if (eventId == seventId)
            galleryEle += eleCur;
    });

    galleryEle += ` </div></div>`;
    document.getElementById('galleryMainCont').innerHTML = galleryEle;
    applyGalleryOwlCarousalJs();

}


function formatDateDDMMYYYY(date) {
    const options = { day: '2-digit', month: 'long', year: 'numeric' };
    return new Intl.DateTimeFormat('en-IN', options).format(date).replace(/\//g, ' ');
}

function formatDateDDMMYY(date) {
    const options = { day: '2-digit', month: '2-digit', year: '2-digit' };
    return new Intl.DateTimeFormat('en-IN', options).format(date).replace(/\//g, '-');
}
function applyGalleryOwlCarousalJs() {
    $('#galleryMain').owlCarousel({
        loop: true,
        margin: 10,
        nav: false,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 2
            },
            1000: {
                items: 3
            }
        }
    });
}

function populateComponents(siteData, sdepttId) {
    let notices = siteData['noticeData'];
    populateTicker(notices, sdepttId);
    applyNewsTickerJs(sdepttId);
}

function populateTicker(notices, sdepttId) {

    let newsTickEle = "";
    let genNoticeEle = ``;
    let admNoticeEle = ``;
    let examNoticeEle = ``;
    let tenderNoticeEle = ``;
    let ignouNoticeEle = ``;
    let depttNoticesEle = ``;
    let noticeDEptEle = ``;
    let noticeModal = ``;


    notices.forEach((notice, index) => {
        const notice_doc_url = "./docs/" + notice['docurl'];
        const notice_title = notice['title'];
        const notice_content = notice['content'];
        const noticeTypeId = notice['notice_type'];
        const datePublished = new Date(notice['published_at']);
        const isPinned = notice['isPinned'];
        const isNew = notice['isNew'];
        const deptt_id = notice['deptt_id'];
        let statusSpinner = '<div class="spinner-grow spinner-grow-sm float-end opacity-25 mt-1 text-dark"></div>';
        let filePinIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pin-angle-fill" viewBox="0 0 16 16"><path d="M9.828.722a.5.5 0 0 1 .354.146l4.95 4.95a.5.5 0 0 1 0 .707c-.48.48-1.072.588-1.503.588-.177 0-.335-.018-.46-.039l-3.134 3.134a6 6 0 0 1 .16 1.013c.046.702-.032 1.687-.72 2.375a.5.5 0 0 1-.707 0l-2.829-2.828-3.182 3.182c-.195.195-1.219.902-1.414.707s.512-1.22.707-1.414l3.182-3.182-2.828-2.829a.5.5 0 0 1 0-.707c.688-.688 1.673-.767 2.375-.72a6 6 0 0 1 1.013.16l3.134-3.133a3 3 0 0 1-.04-.461c0-.43.108-1.022.589-1.503a.5.5 0 0 1 .353-.146"/></svg>`;
        let statusIcon = '<img src = "./images/new.gif" alt = "" ></img>';
        let fileTypeIcon = getFileTypeIcon(notice_doc_url);
        let windowIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-window-desktop" viewBox="0 0 16 16">        <path d="M3.5 11a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5z"/>        <path d="M2.375 1A2.366 2.366 0 0 0 0 3.357v9.286A2.366 2.366 0 0 0 2.375 15h11.25A2.366 2.366 0 0 0 16 12.643V3.357A2.366 2.366 0 0 0 13.625 1zM1 3.357C1 2.612 1.611 2 2.375 2h11.25C14.389 2 15 2.612 15 3.357V4H1zM1 5h14v7.643c0 .745-.611 1.357-1.375 1.357H2.375A1.366 1.366 0 0 1 1 12.643z"/>      </svg>';

        filePinIcon = (isPinned == 1) ? filePinIcon : "";
        statusSpinner = (isNew == 1) ? statusSpinner : "";
        statusIcon = (isNew == 1) ? statusIcon : "";
        let noticeEle = "";
        const showOnHome = notice['showOnHome'];

       
        if (showOnHome == 1) {

            if ((notice['docurl'] == null) || (notice['content'] != null)) {

               // Ignou Notices Not to be Displayed on News Ticker
                if( deptt_id != 38){
                newsTickEle +=
                    `<div class="news-item">
                            <p class="p-0 m-0" data-bs-toggle="modal" data-bs-target="#noticeModal${index}"> ${notice_title}   ${statusIcon}</p>
                    </div> 
                    `;
                }

                noticeEle = `<li class="list-group-item ps-1" data-bs-toggle="modal" data-bs-target="#noticeModal${index}">
                                <span class="pe-0 m-0">  ${windowIcon} </span>
                                <span class="pe-0 m-0"> ${filePinIcon} </span>
                                <span style="font-size:0.9rem; font-weight:bold;"  
                                class="link-body-emphasis  link-offset-2 link-underline-opacity-10 link-underline-opacity-10-hover"
                                class="download-link">
                                <span style="font-size:0.75rem; font-weight:bold;">${formatDateDDMMYY(datePublished)}</span>
                                :&nbsp;${notice_title}
                                ${statusSpinner}
                                </div>
                                </span>                    
                        </li>`;


                noticeModal += ` <div class="modal fade" id="noticeModal${index}" tabindex="-1" aria-labelledby="noticeModalLabel${index}" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h1 class="modal-title fs-5" id="noticeModalLabel${index}">Attention Required</h1>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div id="ticker-content" class="modal-body">
                  ${notice_content}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                  <!-- <button type="button" class="btn btn-primary">Save changes</button> -->
                </div>
              </div>
            </div>
          </div>`;


            } else {

                noticeEle = `<li class="list-group-item ps-1">
                            <span class="pe-0 m-0"> ${fileTypeIcon}</span>
                            <span class="pe-0 m-0"> ${filePinIcon} </span>
                            <a style="font-size:0.9rem; font-weight:bold;"  
                                class="link-body-emphasis  link-offset-2 link-underline-opacity-10 link-underline-opacity-75-hover"
                                href="${notice_doc_url}" class="download-link">
                                <span style="font-size:0.75rem; font-weight:bold;">${formatDateDDMMYY(datePublished)}</span>
                                :&nbsp;${notice_title}
                                ${statusSpinner}
                            </div>
                            </a>
                            </li>`;
            }
        }      
        if (showOnHome == 0 || showOnHome == 1) {
       
            if ((notice['docurl'] == null) || (notice['content'] != null)) {

                    noticeDEptEle = `<li class="list-group-item ps-1" data-bs-toggle="modal" data-bs-target="#noticeModal${index}">
                                <span class="pe-0 m-0">  ${windowIcon} </span>
                                <span class="pe-0 m-0"> ${filePinIcon} </span>
                                <a style="font-size:0.9rem; font-weight:bold;"  
                                class="link-body-emphasis  link-offset-2 link-underline-opacity-10 link-underline-opacity-10-hover"
                                class="download-link">
                                <span style="font-size:0.75rem; font-weight:bold;">${formatDateDDMMYY(datePublished)}</span>
                                :&nbsp;${notice_title}
                                ${statusSpinner}
                                </div>
                                </a>                    
                        </li>`;


                noticeModal += ` <div class="modal fade" id="noticeModal${index}" tabindex="-1" aria-labelledby="noticeModalLabel${index}" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h1 class="modal-title fs-5" id="noticeModalLabel${index}">Attention Required</h1>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div id="ticker-content" class="modal-body">
                  ${notice_content}
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                  <!-- <button type="button" class="btn btn-primary">Save changes</button> -->
                </div>
              </div>
            </div>
          </div>`;


            } else {

                noticeDEptEle = `<li class="list-group-item ps-1">
                            <span class="pe-0 m-0"> ${fileTypeIcon}</span>
                            <span class="pe-0 m-0"> ${filePinIcon} </span>
                            <a style="font-size:0.9rem; font-weight:bold;"  
                                class="link-body-emphasis  link-offset-2 link-underline-opacity-10 link-underline-opacity-75-hover"
                                href="${notice_doc_url}" class="download-link">
                                <span style="font-size:0.75rem; font-weight:bold;">${formatDateDDMMYY(datePublished)}</span>
                                :&nbsp;${notice_title}
                                ${statusSpinner}
                            </div>
                            </a>
                            </li>`;
            }
        }
       

        if (sdepttId == null) {
            switch (noticeTypeId) {
                case 3:
                    genNoticeEle += noticeEle;
                    break;

                case 1:
                    admNoticeEle += noticeEle;
                    break;

                case 2:
                    examNoticeEle += noticeEle;
                    break;

                case 4:
                    tenderNoticeEle += noticeEle;
                    break;

                case 5:
                    ignouNoticeEle += noticeEle;
                    break;

                default:

                    break;
            }
        }
        else if (sdepttId == deptt_id) {
            depttNoticesEle += noticeDEptEle;
        }


    });



    if (sdepttId == null) {
        const newsTickerList = document.getElementById('news-ticker');
        const genNoticeslist = document.getElementById('notices-gen');
        const admNoticeslist = document.getElementById('notices-adm');
        const examNoticeslist = document.getElementById('notices-exam');
        const tenderNoticeslist = document.getElementById('notices-tender');
        const ignouNoticeslist = document.getElementById('notices-ignou');

        newsTickerList.innerHTML = `<div class="news-ticker"> ` + newsTickEle + ` </div>`;
        genNoticeslist.innerHTML = genNoticeEle;
        admNoticeslist.innerHTML = admNoticeEle;
        examNoticeslist.innerHTML = examNoticeEle;
        tenderNoticeslist.innerHTML = tenderNoticeEle;
        ignouNoticeslist.innerHTML = ignouNoticeEle;
        document.getElementById("noticeModal").innerHTML = noticeModal;
    } else {
        const depttNoticeslist = document.getElementById('notices-deptt');
        depttNoticeslist.innerHTML = depttNoticesEle;
        document.getElementById("noticeModal").innerHTML = noticeModal;
    }

}


function applyNewsTickerJs(sdepttId) {
    if (sdepttId == null) {
        const newsTicker = document.querySelector('.news-ticker');
        newsTicker.addEventListener('mouseover', pauseTicker);
        newsTicker.addEventListener('mouseleave', resumeTicker);
    }
}

function pauseTicker() {
    this.style.animationPlayState = 'paused';
}

function resumeTicker() {
    this.style.animationPlayState = 'running';
}

function showLoaderIcons(sdepttId) {
    if (sdepttId == null) {
        $('#loaderGen').show();
        $('#loaderAdm').show();
        $('#loaderExam').show();
        $('#loaderTen').show();
        $('#loaderIgnou').show();
    }
    else {
        $('#loader-deptt').show();
    }
}


function hideLoaderIcons(sdepttId) {
    if (sdepttId == null) {
        $('#loaderGen').hide();
        $('#loaderAdm').hide();
        $('#loaderExam').hide();
        $('#loaderTen').hide();
        $('#loaderIgnou').hide();
    } else {
        $('#loader-deptt').hide();
    }
}

function getFileTypeIcon(notice_doc_url) {

    const fileExtension = notice_doc_url.split('.').pop().toLowerCase();
    const fileTypeIconPdf = '<svg xmlns="http://www.w3.org/2000/svg" aria-label="PDF" role="img" viewBox="0 0 512 512" width="16px" height="16px" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><rect width="512" height="512" rx="15%" fill="#c80a0a"></rect><path fill="#ffffff" d="M413 302c-9-10-29-15-56-15-16 0-33 2-53 5a252 252 0 0 1-52-69c10-30 17-59 17-81 0-17-6-44-30-44-7 0-13 4-17 10-10 18-6 58 13 100a898 898 0 0 1-50 117c-53 22-88 46-91 65-2 9 4 24 25 24 31 0 65-45 91-91a626 626 0 0 1 92-24c38 33 71 38 87 38 32 0 35-23 24-35zM227 111c8-12 26-8 26 16 0 16-5 42-15 72-18-42-18-75-11-88zM100 391c3-16 33-38 80-57-26 44-52 72-68 72-10 0-13-9-12-15zm197-98a574 574 0 0 0-83 22 453 453 0 0 0 36-84 327 327 0 0 0 47 62zm13 4c32-5 59-4 71-2 29 6 19 41-13 33-23-5-42-18-58-31z"></path></g></svg>';
    const fileTypeIconWord = '<svg width="16px" height="16px" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><title>file_type_word2</title><path d="M18.536,2.323V4.868c3.4.019,7.12-.035,10.521.019a.783.783,0,0,1,.912.861c.054,6.266-.013,12.89.032,19.157-.02.4.009,1.118-.053,1.517-.079.509-.306.607-.817.676-.286.039-.764.034-1.045.047-2.792-.014-5.582-.011-8.374-.01l-1.175,0v2.547L2,27.133Q2,16,2,4.873L18.536,2.322" style="fill:#283c82"></path><path d="M18.536,5.822h10.5V26.18h-10.5V23.635h8.27V22.363h-8.27v-1.59h8.27V19.5h-8.27v-1.59h8.27V16.637h-8.27v-1.59h8.27V13.774h-8.27v-1.59h8.27V10.911h-8.27V9.321h8.27V8.048h-8.27V5.822" style="fill:#fff"></path><path d="M8.573,11.443c.6-.035,1.209-.06,1.813-.092.423,2.147.856,4.291,1.314,6.429.359-2.208.757-4.409,1.142-6.613.636-.022,1.272-.057,1.905-.1-.719,3.082-1.349,6.19-2.134,9.254-.531.277-1.326-.013-1.956.032-.423-2.106-.916-4.2-1.295-6.314C8.99,16.1,8.506,18.133,8.08,20.175q-.916-.048-1.839-.111c-.528-2.8-1.148-5.579-1.641-8.385.544-.025,1.091-.048,1.635-.067.328,2.026.7,4.043.986,6.072.448-2.08.907-4.161,1.352-6.241" style="fill:#fff"></path></g></svg>';
    const fileTypeIconExcel = '<svg width="16px" height="16px" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><title>file_type_excel2</title><path d="M28.781,4.405H18.651V2.018L2,4.588V27.115l16.651,2.868V26.445H28.781A1.162,1.162,0,0,0,30,25.349V5.5A1.162,1.162,0,0,0,28.781,4.405Zm.16,21.126H18.617L18.6,23.642h2.487v-2.2H18.581l-.012-1.3h2.518v-2.2H18.55l-.012-1.3h2.549v-2.2H18.53v-1.3h2.557v-2.2H18.53v-1.3h2.557v-2.2H18.53v-2H28.941Z" style="fill:#20744a;fill-rule:evenodd"></path><rect x="22.487" y="7.439" width="4.323" height="2.2" style="fill:#20744a"></rect><rect x="22.487" y="10.94" width="4.323" height="2.2" style="fill:#20744a"></rect><rect x="22.487" y="14.441" width="4.323" height="2.2" style="fill:#20744a"></rect><rect x="22.487" y="17.942" width="4.323" height="2.2" style="fill:#20744a"></rect><rect x="22.487" y="21.443" width="4.323" height="2.2" style="fill:#20744a"></rect><polygon points="6.347 10.673 8.493 10.55 9.842 14.259 11.436 10.397 13.582 10.274 10.976 15.54 13.582 20.819 11.313 20.666 9.781 16.642 8.248 20.513 6.163 20.329 8.585 15.666 6.347 10.673" style="fill:#ffffff;fill-rule:evenodd"></polygon></g></svg>';
    const fileTypeIconUnKnown = `<svg width="16px" height="16px" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <title>file_unknown_fill</title> <g id="é¡µé¢-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"> <g id="File" transform="translate(-864.000000, -240.000000)"> <g id="file_unknown_fill" transform="translate(864.000000, 240.000000)"> <path d="M24,0 L24,24 L0,24 L0,0 L24,0 Z M12.5934901,23.257841 L12.5819402,23.2595131 L12.5108777,23.2950439 L12.4918791,23.2987469 L12.4918791,23.2987469 L12.4767152,23.2950439 L12.4056548,23.2595131 C12.3958229,23.2563662 12.3870493,23.2590235 12.3821421,23.2649074 L12.3780323,23.275831 L12.360941,23.7031097 L12.3658947,23.7234994 L12.3769048,23.7357139 L12.4804777,23.8096931 L12.4953491,23.8136134 L12.4953491,23.8136134 L12.5071152,23.8096931 L12.6106902,23.7357139 L12.6232938,23.7196733 L12.6232938,23.7196733 L12.6266527,23.7031097 L12.609561,23.275831 C12.6075724,23.2657013 12.6010112,23.2592993 12.5934901,23.257841 L12.5934901,23.257841 Z M12.8583906,23.1452862 L12.8445485,23.1473072 L12.6598443,23.2396597 L12.6498822,23.2499052 L12.6498822,23.2499052 L12.6471943,23.2611114 L12.6650943,23.6906389 L12.6699349,23.7034178 L12.6699349,23.7034178 L12.678386,23.7104931 L12.8793402,23.8032389 C12.8914285,23.8068999 12.9022333,23.8029875 12.9078286,23.7952264 L12.9118235,23.7811639 L12.8776777,23.1665331 C12.8752882,23.1545897 12.8674102,23.1470016 12.8583906,23.1452862 L12.8583906,23.1452862 Z M12.1430473,23.1473072 C12.1332178,23.1423925 12.1221763,23.1452606 12.1156365,23.1525954 L12.1099173,23.1665331 L12.0757714,23.7811639 C12.0751323,23.7926639 12.0828099,23.8018602 12.0926481,23.8045676 L12.108256,23.8032389 L12.3092106,23.7104931 L12.3186497,23.7024347 L12.3186497,23.7024347 L12.3225043,23.6906389 L12.340401,23.2611114 L12.337245,23.2485176 L12.337245,23.2485176 L12.3277531,23.2396597 L12.1430473,23.1473072 Z" id="MingCute" fill-rule="nonzero"> </path> <path d="M12,2 L12,8.5 C12,9.32843 12.6716,10 13.5,10 L20,10 L20,20 C20,21.1046 19.1046,22 18,22 L6,22 C4.89543,22 4,21.1046 4,20 L4,4 C4,2.89543 4.89543,2 6,2 L12,2 Z M12,18 C11.4477,18 11,18.4477 11,19 C11,19.5523 11.4477,20 12,20 C12.5523,20 13,19.5523 13,19 C13,18.4477 12.5523,18 12,18 Z M12,12 C10.6193,12 9.5,13.1193 9.5,14.5 C9.5,15.0523 9.94772,15.5 10.5,15.5 C11.0523,15.5 11.5,15.0523 11.5,14.5 C11.5,14.2239 11.7239,14 12,14 C12.2761,14 12.5,14.2239 12.5,14.5 C12.5,14.6589 12.427,14.8002 12.3087,14.8934 C12.0896,15.0661 11.7792,15.3172 11.5252,15.6297 C11.351,15.844 11.1406,16.2239 11.1406,16.5781 C11.1406,16.9324 11.375,17.4219 12,17.4219 C12.4015,17.4219 12.8466,17.0478 13.2543,16.705 C13.3543,16.6209 13.4521,16.5387 13.5464,16.4644 C14.1254,16.0083 14.5,15.2976 14.5,14.5 C14.5,13.1193 13.3807,12 12,12 Z M14,2.04336 C14.3759,2.12295 14.7241,2.30991 15,2.58579 L19.4142,7 C19.6901,7.27588 19.8771,7.62406 19.9566,8 L14,8 L14,2.04336 Z" id="å½¢ç¶ç»å" fill="#09244B"> </path> </g> </g> </g> </g></svg>`;
    const fileTypeIconImage = `<svg width="16px" height="16px" viewBox="-4 0 64 64" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g fill-rule="evenodd" clip-rule="evenodd"> <path d="M5.125.042c-2.801 0-5.072 2.273-5.072 5.074v53.841c0 2.803 2.271 5.073 5.072 5.073h45.775c2.801 0 5.074-2.271 5.074-5.073v-38.604l-18.904-20.311h-31.945z" fill="#49C9A7"></path> <path d="M55.977 20.352v1h-12.799s-6.312-1.26-6.129-6.707c0 0 .208 5.707 6.004 5.707h12.924z" fill="#37BB91"></path> <path d="M37.074 0v14.561c0 1.656 1.104 5.791 6.104 5.791h12.799l-18.903-20.352z" opacity=".5" fill="#ffffff"></path> </g> <path d="M10.119 53.739v-20.904h20.906v20.904h-20.906zm18.799-18.843h-16.691v12.6h16.691v-12.6zm-9.583 8.384l3.909-5.256 1.207 2.123 1.395-.434.984 5.631h-13.082l3.496-3.32 2.091 1.256zm-3.856-3.64c-.91 0-1.649-.688-1.649-1.538 0-.849.739-1.538 1.649-1.538.912 0 1.65.689 1.65 1.538 0 .85-.738 1.538-1.65 1.538z" fill-rule="evenodd" clip-rule="evenodd" fill="#ffffff"></path> </g></svg>`;
    let fileTypeIcon = "";

    // Check the file extension
    if (fileExtension === 'pdf') {
        fileTypeIcon = fileTypeIconPdf;
    } else if (['doc', 'docx'].includes(fileExtension)) {
        fileTypeIcon = fileTypeIconWord
    } else if (['xls', 'xlsx'].includes(fileExtension)) {
        fileTypeIcon = fileTypeIconExcel;
    } else if (['png', 'jpg', 'jpeg'].includes(fileExtension)) {
        fileTypeIcon = fileTypeIconImage;
    } else {
        fileTypeIcon = fileTypeIconUnKnown;
    }

    return (fileTypeIcon);
}

export function getAndPopulateEventReport(depttId, eventId, supEventType) {

    fetchEvents();
    function fetchEvents() {
        $.ajax({
            url: './src/fetchEvents.php',
            type: 'get',
            data: { null: null },
            dataType: 'json',
            beforeSend: function () {
                showLoaderIcons();
            },
            complete: function () {
                hideLoaderIcons();
            },
            success: function (response) {
                if (response['sliderData'] != "") {
                    populateEventReportComponent(response['sliderData'], depttId, eventId, supEventType);
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                alert("Oops! Something went wrong while fetching siteD Data");
            }

        });
    }
}


function populateEventReportComponent(eventDetails, depttId, supEventId, supEventType) {

    eventDetails.forEach((eventRow) => {
        let eid = eventRow['id']
        let eventTitle = eventRow['title'];
        let eventReport = eventRow['content'];
        let eventType = eventRow['eventType'];
        const datePublished = new Date(eventRow['published_at']);
        let dateLabel = (eventType == 3) ? "Scheduled: " : "Dated: ";

        if (supEventType == 3 && eid == supEventId) {
            document.getElementById("broucherLink").href = "./docs/" + `${eventRow['broucherLink']}`;
            document.getElementById("regLink").href = `${eventRow['regLink']}`;
        }

        if (eid == supEventId) {
            document.getElementById('eventTitle').innerHTML = `
                                    <h2>${eventTitle}</h2>
                                    <h3> ${dateLabel} ${formatDateDDMMYYYY(datePublished)} </h3>`;
            document.getElementById('eventReport').innerHTML = eventReport;

        }
    });

}


export function getAndPopulateEventsSlider(depttId, eventType, containerId) {

    fetchEvents();

    function fetchEvents() {
        $.ajax({
            url: './src/fetchEvents.php',
            type: 'get',
            data: { null: null },
            dataType: 'json',
            beforeSend: function () {
                showLoaderIcons();
            },
            complete: function () {
                hideLoaderIcons();
            },
            success: function (response) {
                if (response['sliderData'] != "") {
                    populateEventsSlider(response['sliderData'], depttId, eventType, containerId);
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                alert("Oops! Something went wrong while fetching Events Data");
            }
        });
    }

}

function populateEventsSlider(eventDetails, supDepttId, supEventType, containerId) {


    let sliderBodyId = "SliderTpe" + supEventType + "" + containerId;
    let sliderEle = `<div id="${sliderBodyId}" class="owl-carousel">`;
    let curSlideEle = null;
    const slideCaption = (supEventType == 2) ? "Reflections" : (supEventType == 3) ? "Upcomming Events" : "Event?";
    const slideCaptionColor = (supEventType == 2) ? "bg-secondary" : (supEventType == 3) ? "bg-success" : "bg-danger";

    eventDetails.forEach((slide) => {
        const slider_title = slide['title'];
        const parentDeptt = slide['deptt_id'];
        const eventType = slide['eventType']
        const slider_briefDes = getLeadPara(slide['briefDes']);
        const imgThumbNail = "./images/" + slide['imgThumbNail'];
        const leadImg = "./images/" + slide['imgFile1'];
        const eid = slide['id'];
        let showOnHome = slide['showOnHome'];
        let eventDetailPage = (eventType == 2) ? "pevents.php" : (eventType == 3) ? "fevents.php" : "unknown.php";
        const slideMoreButCaption = (eventType == 2) ? " Read more..." : "Details...";

        curSlideEle = `<div class="item">
                                <div class="card">
                                    <img src="${imgThumbNail}" class="card-img-top" alt="Image 1">
                                    <div class="card-body" style="max-height:500px;">
                                        <h5 class="card-title">${slider_title}</h5>
                                        <p class="card-text">  ${slider_briefDes}</p>                                        
                                    </div>
                                    <div class="card-body pt-0 mt-0">
                                    <a href="${eventDetailPage}?eid=${eid}" class=" float-start link-success link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover fw-bolder">${slideMoreButCaption}</a>
                                    </div>

                                </div>

                            </div>  `
            ;

        // if events are of Particular Type(Past/Future...) and are belonging to any Department (Suited for Home page Events Provided Has Home Page Visibility)
        if (eventType == supEventType && supDepttId == null && showOnHome == 1) {
            sliderEle += curSlideEle;
        }
        else
            // if events are of Particular Type(Past/Future...) and are belonging to the Department called for                    
            if (eventType == supEventType && parentDeptt == supDepttId) {
                sliderEle += curSlideEle;
            }

    });


    sliderEle += `</div>`;

    let sliderHeaderId = "slideHeader" + supEventType + "" + containerId;


    const sliderHeaderWithButtons = `<div id="${sliderHeaderId}">                
                                        <div class="${slideCaptionColor} text-white p-2 m-0">
                                            <span style="font-weight:700; font-size: 22px;; padding-left:5px;">${slideCaption}</span> 
                                            <span class="btn-prev"> 
                                                <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">
                                                    <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0"/>
                                                </svg>
                                            </span>
                                            <span class=" btn-next">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">
                                                    <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708"/>
                                                </svg>
                                            </span>
                                        </div>
                                    </div>`;


    let h = ` <div class="card p-0 my-3">            
                              <div    class="card-body p-0">`;

    document.getElementById(`${containerId}`).innerHTML = h + sliderHeaderWithButtons + sliderEle + "</div></div>";
    applySlideToOwlCarousal(sliderBodyId, sliderHeaderId);

}

function getLeadPara(content) {

    let mxLen = 250;
    let lp = content.substring(0, mxLen);
    lp += '^'.repeat(mxLen - lp.length);
    lp = lp.replace(/\^/g, '&nbsp;');
    return lp;
}


function applySlideToOwlCarousal(sliderBodyId, sliderHeaderId) {

    $(`#${sliderBodyId}`).owlCarousel({
        items: 3,
        loop: true,
        margin: 10,
        nav: false,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 2
            },
            1000: {
                items: 3
            }
        }
    });

    $(`#${sliderHeaderId} .btn-prev`).click(function () {
        $(`#${sliderBodyId}`).trigger("prev.owl.carousel");
    });

    $(`#${sliderHeaderId} .btn-next`).click(function () {
        $(`#${sliderBodyId}`).trigger("next.owl.carousel");
    });
}

export function getAndPopulateDepartmentsMenu() {


    fetchDepartments();

    function fetchDepartments() {
        $.ajax({
            url: './src/fetchDepartments.php',
            type: 'get',
            data: { null: null },
            dataType: 'json',
            beforeSend: function () {
                showLoaderIcons();
            },
            complete: function () {
                hideLoaderIcons();
            },
            success: function (response) {
                if (response['deptProfile'] != "") {
                    PopulateDepartmentsMenu(response['deptProfile']);
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 
                alert("Oops! Something went wrong while fetching Departments Data");
            }
        });
    }

}

function PopulateDepartmentsMenu(departments) {

    let listEle = "";
    departments.forEach((department) => {
        const did = department["id"];
        const dname = department["name"];
        const isAcademic = department["is_academic"];
        const isUg = department["is_ug"];
        const isPg = department["is_pg"];
        if (isAcademic == 1 && (isUg == 1 || isPg == 1))
            listEle += `<li><a  class="dropdown-item" href="./departments.php?id=${did}">${dname} </a></li>`;
    });
    document.getElementById("departmentsListId").innerHTML = listEle;
}


export function getAndPopulateDepartmetContent(supDepttId) {

    // Needs to Call a function which will Fetch Department Centent
    fetchDepartments();

    function fetchDepartments() {
        $.ajax({
            url: './src/fetchDepartments.php',
            type: 'get',
            data: { null: null },
            dataType: 'json',
            beforeSend: function () {
                showLoaderIcons();
            },
            complete: function () {
                hideLoaderIcons();
            },
            success: function (response) {
                if (response['deptProfile'] != "") {
                    PopulateDepartmentsContent(response['deptProfile'], supDepttId);
                    // alert("Oops! Department Content is not Available");              
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //  alert("Status: " + textStatus); alert("Error: " + errorThrown); 

            }
        });
    }


}

function PopulateDepartmentsContent(departmentProfile, supDepttId) {

    let dname = "";
    departmentProfile.forEach((department) => {
        const did = department["id"];
        dname = department["name"];
        if (supDepttId == did) {
            document.getElementById("deptName").innerHTML = dname;
            return;
        }

    });
}

export function fetchData(url, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        type: 'GET',
        data: data,
        dataType: 'json',
        cache: false,
        success: successCallback,
        error: errorCallback
    });
};


export function populateSections(sectionId, data) {
    data.forEach((item, index) => {
        let sectionTitle = item['sectionTitle'];
        let section_id = item['section_id'];
        let dynamicSectionId = "Section-" + section_id;        
        let collapseId = "collapse-" + section_id;      
        let headingId = "heading-" + section_id; 

        // First item open by default
        let isFirst = index === 0;
        let showClass = isFirst ? 'show' : '';
        let collapsedClass = isFirst ? '' : 'collapsed';
        let expandedAttr = isFirst ? 'true' : 'false';

        let sectionTemplate = `
            <div class="accordion-item my-2">
                <p class="accordion-header p-0" id="${headingId}">
                    <button class="accordion-button ${collapsedClass} bg-body-secondary" type="button"
                        data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="${expandedAttr}"
                        aria-controls="${collapseId}">
                        <h2>${sectionTitle}</h2>
                    </button>
                </p>
                <div id="${collapseId}" class="accordion-collapse collapse ${showClass}" aria-labelledby="${headingId}">
                    <div id="${dynamicSectionId}" class="accordion-body">
                        ${item['sectionDescription']}
                    </div>
                </div>
            </div>`;

        $('#noticeboard').append(sectionTemplate);
        $(`#${dynamicSectionId}`).addClass('lower-font');
    });
};



export function populateStaffSection(sectionId, data) {


    let profileCard = "";


    data.forEach(employee => {


        let hodLabel = (employee.is_hod == 1) ? "&amp;&nbspHOD" : ""

        profileCard += ` <!-- Faculty- 1 card Starts-->
            <div class="col-md-3 pb-4">        
                   
                        <div class="card bg-light">
 
                             <div class="card-header">       
                                 <div style="display: flex;flex-direction: column; align-items: center;">
                                         <div class="card-body p-0">
                                             <img src="images/${employee.photo_url}"   class= "rounded-circle" height = "105px;"   alt="Photograph">
                                         </div>
                                 </div> 
                             </div>
                           
                             <div class="card-body pt-2">                    
                                     <ul class="list-group list-group-flush" id="facultydetails" style="list-style-type: none;">
                                         <li style="font-weight: 800; font-size:22px; margin-left:-18px;"> &nbsp; <b>${employee.fullname}</b></li>
                                         <li><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-briefcase-fill" viewBox="0 0 16 16">
                                         <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v1.384l7.614 2.03a1.5 1.5 0 0 0 .772 0L16 5.884V4.5A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5"/>
                                         <path d="M0 12.5A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5V6.85L8.129 8.947a.5.5 0 0 1-.258 0L0 6.85z"/>
                                       </svg> &nbsp; <b>${employee.designation}&nbsp;${hodLabel}</b></li>
                                           <li><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-envelope" viewBox="0 0 16 16">
                                         <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1zm13 2.383-4.708 2.825L15 11.105zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741M1 11.105l4.708-2.897L1 5.383z"/>
                                       </svg> &nbsp; ${employee.emailid}</li>
                                           <li><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-backpack-fill" viewBox="0 0 16 16">
                                         <path d="M5 13v-3h4v.5a.5.5 0 0 0 1 0V10h1v3z"/>
                                         <path d="M6 2v.341C3.67 3.165 2 5.388 2 8v5.5A2.5 2.5 0 0 0 4.5 16h7a2.5 2.5 0 0 0 2.5-2.5V8a6.002 6.002 0 0 0-4-5.659V2a2 2 0 1 0-4 0m2-1a1 1 0 0 1 1 1v.083a6.04 6.04 0 0 0-2 0V2a1 1 0 0 1 1-1m0 3a4 4 0 0 1 3.96 3.43.5.5 0 1 1-.99.14 3 3 0 0 0-5.94 0 .5.5 0 1 1-.99-.14A4 4 0 0 1 8 4M4.5 9h7a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5"/>
                                       </svg> &nbsp; ${employee.highestQualif}</li>
                                     </ul>
                             </div>
                           
                             <div class="card-footer text-center p-0">
                                 <a href="./docs/${employee.cv_url}" class="card-link"> Download CV</a> 
                             </div>
                            
                       </div>
             </div>
 
            <!-- Faculty- 1 card Ends-->`;



    });


    document.getElementById(sectionId).innerHTML = (profileCard);

};

