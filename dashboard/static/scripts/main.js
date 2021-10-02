mapboxgl.accessToken = 'pk.eyJ1IjoicGFuZ2VhbWFwcyIsImEiOiJjaWdra3A1bjgwMHRwdW5senp6ajZzN2Z5In0.pZv62GV1KFSFmcnJqMCnFQ';

let leadId = 0;
let leadIndex = 0;
let leadType = "New"
let leads = null;
let activeLead = {center: {lat: -27.3, lng: 153.0}, zoom: 9, emails: undefined};
let emails;
let emailReq = new XMLHttpRequest();
let startup = true;
let dimensions = {metric: ['430x430', '600x600', '830x830'], imperial: ['17.5x17.5', '24x24', '32x32']};
let pending = {
    New: [],
    Quoted: [],
    Design: [],
    Invoice: [],
    Production: [],
    Other: []
};
let unread = true;

let map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/pangeamaps/cjrfg2xig6upe2sp22iztvgs8',
    center: activeLead.center,
    zoom: 9
});
let marker = new mapboxgl.Marker({draggable: true});
marker.on('dragend', () => {
    let lngLat = marker.getLngLat();
    $("#LeadMark").val(lngLat.lat.toFixed(4) + ', ' + lngLat.lng.toFixed(4));
})

function setSizes(unit) {
    let sizeOptions = $("#LeadSizeOptions")[0].options;
    for (let i = 0; i < sizeOptions.length; i++) {
        sizeOptions[i].innerText = dimensions[unit][i];
        sizeOptions[i].value = i;
    }
}

function hostUrl() {
    let baseurl = location.protocol + '//' + location.host + '/';
    return baseurl;
}

function setStatus(status, next) {
    let url = hostUrl() + 'status/' + activeLead.id + '/' + status;
    let req = new XMLHttpRequest();
    req.open("PUT", url);
    req.send();
    if (next) {
        markRead()
        nextLead();
    } else getLead(activeLead.id);
}

function markRead() {
    let url = hostUrl() + 'read/' + activeLead.email;

    let req = new XMLHttpRequest();
    req.open("GET", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            console.log('emails read');
        }
    }
    req.send();
}

function sendEmail(action) {
    let url = hostUrl() + 'send/' + activeLead.id;
    let headerEmail = $("#HeaderEmail")[0];
    action.innerText = "SENDING";
    action.onclick = null;

    let req = new XMLHttpRequest();
    req.open("POST", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            action.innerText = "QUEUED";
            if (activeLead.state < 200) {
                setStatus(200, true);
            } else if (activeLead.state < 300) {
                setStatus(300, true);
            } else {
                nextLead();
            }
        }
    }
    req.send(JSON.stringify({body: headerEmail.innerText, id: activeLead.msgid, subject: activeLead.subject}));
    headerEmail.contentEditable = "false";
    headerEmail.innerText = "Loading";
}

function draftEmail(emailType, action) {
    let url = hostUrl() + 'draftemail/' + activeLead.id + '/' + emailType;
    let req = new XMLHttpRequest();
    req.open("GET", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            let draft = JSON.parse(req.response);
            let headerEmail = $("#HeaderEmail")[0];
            headerEmail.contentEditable = "true";
            headerEmail.innerText = draft.body;
            action.innerText = "SEND";
            action.onclick = () => {
                sendEmail(action)
            };
        }
    }
    req.send();
}

function mapResize() {
    let mapBox = $("#map")[0];
    let h1 = mapBox.clientHeight;
    let h = $("#BoundaryBox")[0].clientHeight;
    let top = $("#BoundaryBox")[0].offsetTop;
    let h2 = h + 2 * top;
    let w1 = mapBox.clientWidth;
    let w2 = $("#parent")[0].clientWidth + 16;
    let center = map.project(map.getCenter());
    mapBox.style.height = h2;
    mapBox.style.width = w2;
    map.resize();
    center.x += (w2 - w1) / 2;
    center.y += (h2 - h1) / 2;
    map.setCenter(map.unproject(center));
}

function changeLead(index) {
    leadIndex = index;
    getLead(leads[leadType][leadId].leads[index]);
    for (let i = 0; i < leads[leadType][leadId].leads.length; i++) {
        $("#Lead" + i).css("color", "black");
        if (i == index) {
            $("#Lead" + i).css("color", "#cfb28a");
        }
    }
}

function createLead(leadEmail) {
    activeLead = {};
    activeLead.email = leadEmail;
    activeLead.id = 'new';
    activeLead.msgid = leads[leadType][leadId].msgid;
    activeLead.subject = leads[leadType][leadId].subject;
    activeLead.map = $("#LeadLabel").valueOf();
    $("#LabelRadioButton")[0].children[0].checked = true;
    activeLead.name = $("#LeadName").val();
    $("#LeadNameRadioButton")[0].children[0].checked = true;
    updateBoundary()
}

function updateBoundary() {
    let bb = $("#BoundaryBox")[0];
    let p1 = {x: bb.offsetLeft, y: bb.offsetTop};
    let p2 = {x: p1.x + bb.clientWidth, y: p1.y + bb.clientHeight};
    let topLeft = map.unproject(p1);
    let bottomRight = map.unproject(p2);
    activeLead.topLeft = topLeft;
    activeLead.bottomRight = bottomRight;
    activeLead.zoom = map.getZoom();
    activeLead.center = map.getCenter();
    updateLead();
}

function updateLead(action) {
    let name = $("#LeadNameRadioButton")[0].children[0].checked;
    let label = $("#LabelRadioButton")[0].children[0].checked;
    let mark = $("#MarkRadioButton")[0].children[0].checked;
    let units = $("#UnitsRadioButton")[0].children[0].checked;
    let size = $("#SizeRadioButton")[0].children[0].checked;
    let country = $("#ShippingCountryRadio")[0].children[0].checked;
    let address = $("#ShippingAddressRadio")[0].children[0].checked;
    let phonenumber =  $("#PhoneNumberRadio")[0].children[0].checked;
    let render = $("#RenderRadioButton")[0].children[0].checked;
    let invoice = $("#InvoiceRadioButton")[0].children[0].checked;
    let price = $("#PriceRadioButton")[0].children[0].checked;
    let currency = $("#CurrencyRadioButton")[0].children[0].checked;
    let description = $("#DescriptionRadioButton")[0].children[0].checked;
    let production = $("#ProductionRadioButton")[0].children[0].checked;
    let boundary = (activeLead.bottomRight && activeLead.topLeft);
    let updates = {
        "email": activeLead.email,
    }
    if (mark) {
        let latlng = JSON.parse('[' + $("#LeadMark").val() + ']');
        updates.poi = {lat: latlng[0], lng: latlng[1]};
    }
    if (units) {
        if ($("#Metric").val()) {
            updates.units = "metric";
        } else {
            updates.units = "imperial";
        }
    }
    if (render) {
        if ($("#Render").val()) {
            updates.render = $("#RenderValue").val();
        } else {
            updates.render = "https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/Pangea.png";
        }
    }
    if (size) updates.size = $("#LeadSize").val();
    if (address) {
        let address = $("#LeadAddress").val().split(',');
        updates.address = {};
        updates.address.line1 = address[0];
        updates.address.city = address[1];
        updates.address.state = address[2];
        updates.address.postal_code = address[3];
        if (country) updates.address.country = $("#LeadCountry").val();
    }
    if (invoice) updates.invoice = $("#LeadInvoice").val();
    if (price) updates.price = $("#LeadPrice").val();
    if (phonenumber) updates.phonenumber = $("#LeadNumber").val();
    if (currency) updates.currency = $("#LeadCurrency").val().toLowerCase();
    if (description) updates.description = $("#LeadDescription").val();
    if (production) updates.production = $("#LeadProduction").val();
    if (label) updates.mapName = $("#LeadLabel").val();
    if (name) updates.firstName = $("#LeadName").val();
    if (boundary) {
        updates.topLeft = activeLead.topLeft;
        updates.bottomRight = activeLead.bottomRight;
        updates.mapZoom = map.getZoom();
        updates.center = map.getCenter();
    }
    let url = hostUrl() + 'lead/' + activeLead.id;
    let req = new XMLHttpRequest();
    req.open("PUT", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            let response = JSON.parse(req.response);
            if (action === undefined) {
                getLead(response.id);
            } else {
                action();
            }
        }
    }
    req.send(JSON.stringify(updates));
}

function selectLead() {
    let total;
    let leadDetails = $('#LeadNumbers')[0];
    leadDetails.innerHTML = '';
    let parent = $("#Emails")[0];
    parent.innerHTML = "";
    let header = $("#HeaderEmail")[0];
    header.innerText = "Loading";
    if (unread) {
        console.log('selecting lead: ' + leadId)
        let lead = leads[leadType][leadId].leads;
        let leadEmail = leads[leadType][leadId].email;
        if (lead.length === 0) {
            leadDetails.innerHTML = '<span class="LeadLink" id="CreateLead"> Create Lead</span><br>';
            $("#CreateLead").click(() => {
                createLead(leadEmail);
            });
            clearLead(leadEmail);
            deleteContours();
            marker.remove();
            header.innerText = "No Lead";
            getEmail(leadEmail);
        } else {
            for (let i = 0; i < lead.length; i++) {
                leadDetails.innerHTML += '<span class="LeadLink" id="Lead' + i + '" onclick="changeLead(' + i + ')">' + lead[i] + '</span>,'
                if (i == 0) {
                    $("#Lead" + i).css("color", "#cfb28a");
                }
            }
            leadDetails.innerHTML += '<br>'
            getLead(leads[leadType][leadId].leads[leadIndex]);
        }
        total = Object.keys(leads[leadType]).length;
    } else {
        getLead(pending[leadType][leadId]);
        total = pending[leadType].length;
    }
    $("#Counter")[0].innerText = (leadId + 1) + "/" + total;
}

function getLeads() {
    let leadURL = document.location.href + "leads";
    let leadReq = new XMLHttpRequest();
    leadReq.open("GET", leadURL);
    leadReq.onreadystatechange = () => {
        if (leadReq.readyState === XMLHttpRequest.DONE) {
            try {
                leads = JSON.parse(leadReq.response);
                $("#Counter")[0].innerText = (leadId + 1) + "/" + Object.keys(leads[leadType]).length;
                $("#New")[0].innerText = "NEW LEADS: " + Object.keys(leads.New).length;
                $("#Quoted")[0].innerText = "QUOTED LEADS: " + Object.keys(leads.Quoted).length;
                $("#Design")[0].innerText = "DESIGNED LEADS: " + Object.keys(leads.Design).length;
                $("#Invoiced")[0].innerText = "INVOICED LEADS: " + Object.keys(leads.Invoice).length;
                $("#Production")[0].innerText = "IN PRODUCTION LEADS: " + Object.keys(leads.Production).length;
                $("#Other")[0].innerText = "OTHER: " + Object.keys(leads.Other).length;
                if (startup) {
                    getLeadType("New");
                    startup = false;
                }
            } catch (e) {

            }
        }
    }
    leadReq.send();
}

function getEmail(emailId) {
    let emailUrl = document.location.href + "emails/" + emailId;
    let parent = $("#Emails")[0];
    parent.innerHTML = "";

    emailReq.abort();
    emailReq = new XMLHttpRequest();
    emailReq.open("GET", emailUrl);
    emailReq.onprogress = () => {
        let part_response = emailReq.response.split('\n');
        emails = []
        for (let i = 0; i < part_response.length; i++) {
            if (part_response[i]) {
                let email = JSON.parse(part_response[i]);
                emails.push(email);
            }
        }
        emails.sort((a, b) => {
            const a_ = a.timestamp;
            const b_ = b.timestamp;
            if (a_ == b_) return 0; else if (a_ > b_) return -1; else return 1
        });
        if (emails.length > 0) {
            parent.innerHTML = '';
            for (let i = 0; i < emails.length; i++) {
                let email = emails[i]
                let leadList = $('<div></div>').attr({class: "Email"});
                let innerHTML = email.body.split(">")[0].replace(/\n|\r/g, "<br />");
                leadList.html(innerHTML);
                if (!email.flags.includes("SEEN")) {
                    leadList.css("backgroundColor", "#afafaf");
                } else if (email.from.search("pangeamaps.com") > 0) {
                    leadList.css("backgroundColor", "#897a51");
                }
                parent.appendChild(leadList[0]);
            }
        }
    }
    emailReq.send();
}

function clearLead(leadEmail) {
    $("#Name")[0].innerText = "";
    $("#LeadType")[0].innerText = "-";
    $("#Email").val(leadEmail)
    $("#EmailDetail").val(leadEmail)
    $("#Id").val('');
    $("#IdDetail").val('');
    $("#MapName").text("No Lead");
    $("#DesignBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/black.png';
    $("#DataBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/black.png';
    $("#DataBoxLink")[0].href = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/black.png';
    $("#LabelButton")[0].href = '';
    $("#DownloadButton")[0].href = '';
    $("#LeadName").val('');
    $("#LeadMark").val('');
    $("#LeadLabel").val('');
    $("#Metric").css("color", "#fafafa")
    $("#Imperial").css("color", "#897a51")
    $("#LeadSize").val('');
    $("#ShippingCountry").val('');
    $("#ShippingAddress").val('');
    $("#Invoice").val('');
    $("#Price").val('');
    $("#PhoneNumber").val('');
    $("#Currency").val('');
    $("#Description").val('');
    $("#ProductionCountry").val('');

    map.setZoom(activeLead.zoom);
    setMapboxCenter(activeLead.center);

    deleteContours();
    drawContours(activeLead.hash);
    toggleProgress(true);
    let progressElements = ["#BoundaryButton",
        "#QuotedButton",
        "#DesignButton",
        "#InvoiceButton",
        "#PaidButton",
        "#ProductionButton"]
    progressElements.forEach(element =>
        $(element).css("backgroundColor", "#cfb28a")
    );
    let action_button = $("#ActionButton");
    action_button.text("Send Quote");
    action_button.click(() => {
        draftEmail("Quote", action_button)
    });
    let special_button = $("#SpecialButton");
    special_button.text("Send Email");
    special_button.click(() => {
        draftEmail("Compose", special_button)
    });
    getEmail(leadEmail);
}

function getLead(leadId) {
    let items = $(".UpdateCheck");
    for (let i = 0; i < items.length; i++) {
        items[i].checked = false;
    }
    let url = document.location.href + "lead/" + leadId;
    let req = new XMLHttpRequest();
    req.open("GET", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            activeLead = JSON.parse(req.response);
            console.log(activeLead);
            if (activeLead.id) {
                $("#HeaderEmail")[0].contentEditable = 'false';
                $("#HeaderEmail").html(activeLead.emails.body.replace(/(<([^>]+)>)/ig, "").replace(/\n|\r/g, "<br>"))
                $("#Name").text(activeLead.name)
                $("#LeadType").text(activeLead.total)
                $("#Email").val(activeLead.email)
                $("#EmailDetail").val(activeLead.email)
                $("#Id").val(activeLead.id)
                $("#IdDetail").val(activeLead.id)
                $("#MapName").text(activeLead.map)
                if (leadType == "New") {
                    $("#DesignBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/black.png';
                    $("#DataBox")[0].src = 'https://www.pangeamaps.com/boundaries/' + leadId + '/bounds.jpg';
                    $("#DataBoxLink")[0].href = 'https://www.pangeamaps.com/boundaries/' + leadId + '/bounds.jpg';
                } else {
                    $("#DesignBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/' + activeLead.map + '_canvas.png';
                    $("#DataBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/raster.png';
                    $("#DataBoxLink")[0].href = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/raster.png';
                    $("#LabelButton")[0].href = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/' + activeLead.map + '_label.png';
                    $("#DownloadButton")[0].href = hostUrl() + 's3/pangea-render-data/' + activeLead.hash + '/' + activeLead.map + '_' + (activeLead.size.split('x')[0]) + (activeLead.units == "metric" ? "mm" : "in") + '.zip';
                    $("#RenderValue").val('https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/' + activeLead.map + '_canvas.png');
                }
                $("#LeadName").val(activeLead.name)
                if (activeLead.mark.lat && activeLead.mark.lng) {
                    $("#LeadMark").val(activeLead.mark.lat.toFixed(4) + ', ' + activeLead.mark.lng.toFixed(4));
                    marker.setLngLat(activeLead.mark).addTo(map);
                }
                $("#LeadLabel").val(activeLead.map);
                if (activeLead.units == "metric") {
                    $("#Metric").val(true)
                    $("#Metric").css("color", "#fafafa")
                    $("#Imperial").css("color", "#897a51")
                    setSizes('metric');
                } else {
                    $("#Metric").val(false)
                    $("#Metric").css("color", "#897a51")
                    $("#Imperial").css("color", "#fafafa")
                    setSizes('imperial');
                }
                if (activeLead.render == $("#RenderValue").val()) {
                    $("#Render").val(true)
                    $("#Render").css("color", "#fafafa")
                    $("#Logo").css("color", "#897a51")
                } else {
                    $("#Render").val(false)
                    $("#Render").css("color", "#897a51")
                    $("#Logo").css("color", "#fafafa")
                }
                $("#LeadSize").val(activeLead.size);
                $("#LeadCountry").val(activeLead.address.country);
                $("#LeadAddress").val(activeLead.address.line1 + "," + activeLead.address.city + "," + activeLead.address.state + "," + activeLead.address.postal_code);
                $("#LeadInvoice").val(activeLead.invoice);
                $("#LeadPrice").val(activeLead.price);
                $("#LeadNumber").val(activeLead.phonenumber);
                console.log(activeLead.phonenumber)
                $("#LeadCurrency").val(activeLead.currency.toUpperCase());
                $("#LeadDescription").val(activeLead.description);
                $("#LeadProduction").val(activeLead.production);

                map.setZoom(activeLead.zoom);
                setMapboxCenter(activeLead.center);

                deleteContours();
                drawContours(activeLead.hash);
                toggleProgress(true);
                let special_button = $("#SpecialButton")[0];
                special_button.innerText = "Send Email";
                special_button.onclick = () => {
                    draftEmail("Compose", special_button)
                };

                if (activeLead.state < 200) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#cfb28a")
                    $("#DesignButton").css("backgroundColor", "#cfb28a")
                    $("#InvoiceButton").css("backgroundColor", "#cfb28a")
                    $("#PaidButton").css("backgroundColor", "#cfb28a")
                    $("#ProductionButton").css("backgroundColor", "#cfb28a")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Quote";
                    action_button.onclick = () => {
                        draftEmail("Quote", action_button)
                    };
                } else if (activeLead.state < 300) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#cfb28a")
                    $("#InvoiceButton").css("backgroundColor", "#cfb28a")
                    $("#PaidButton").css("backgroundColor", "#cfb28a")
                    $("#ProductionButton").css("backgroundColor", "#cfb28a")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Render";
                    action_button.onclick = () => {
                        draftEmail("Render", action_button)
                    };
                } else if (activeLead.state < 400) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#000000")
                    $("#InvoiceButton").css("backgroundColor", "#cfb28a")
                    $("#PaidButton").css("backgroundColor", "#cfb28a")
                    $("#ProductionButton").css("backgroundColor", "#cfb28a")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Invoice";
                    action_button.onclick = () => {
                        draftEmail("Invoice", action_button)
                    };
                } else if (activeLead.state < 500) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#000000")
                    $("#InvoiceButton").css("backgroundColor", "#000000")
                    $("#PaidButton").css("backgroundColor", "#cfb28a")
                    $("#ProductionButton").css("backgroundColor", "#cfb28a")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Email";
                    action_button.onclick = () => {
                        draftEmail("Quote", action_button)
                    };
                } else if (activeLead.state < 600) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#000000")
                    $("#InvoiceButton").css("backgroundColor", "#000000")
                    $("#PaidButton").css("backgroundColor", "#000000")
                    $("#ProductionButton").css("backgroundColor", "#cfb28a")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Email";
                    action_button.onclick = () => {
                        draftEmail("Other", action_button)
                    };
                } else if (activeLead.state < 700) {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#000000")
                    $("#InvoiceButton").css("backgroundColor", "#000000")
                    $("#PaidButton").css("backgroundColor", "#000000")
                    $("#ProductionButton").css("backgroundColor", "#000000")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Email";
                    action_button.onclick = () => {
                        draftEmail("Other", action_button)
                    };
                } else {
                    $("#BoundaryButton").css("backgroundColor", "#000000")
                    $("#QuotedButton").css("backgroundColor", "#000000")
                    $("#DesignButton").css("backgroundColor", "#000000")
                    $("#InvoiceButton").css("backgroundColor", "#000000")
                    $("#PaidButton").css("backgroundColor", "#000000")
                    $("#ProductionButton").css("backgroundColor", "#000000")
                    let action_button = $("#ActionButton")[0];
                    action_button.innerText = "Send Email";
                    action_button.onclick = () => {
                        draftEmail("Other", action_button)
                    };
                }
            }
        }
    }
    req.send();
    getEmail(leadId);
}

function getLeadEmail() {
    let emailElem = $("#Email").val();
    if (emailElem !== activeLead.email) {
        getLead(emailElem);
    }
}

function getLeadEmailDetail() {
    let emailElem = $("#EmailDetail").val();
    if (emailElem !== activeLead.email) {
        getLead(emailElem);
    }
}


function getLeadId() {
    let leadIdElem = $("#Id").val();
    if (leadIdElem !== activeLead.id) {
        getLead(leadIdElem);
    }
}


function getLeadIdDetail() {
    let leadIdElem = $("#IdDetail").val();
    if (leadIdElem !== activeLead.id) {
        getLead(leadIdElem);
    }
}

function setMapboxCenter(mapCenterLL) {
    map.setCenter(mapCenterLL);
    let center = map.project(map.getCenter());
    let boundingBoxCenter = getBoundaryBoxCenter();
    let newCenter = {x: 2 * center.x - boundingBoxCenter.x, y: 2 * center.y - boundingBoxCenter.y};
    map.setCenter(map.unproject(newCenter));
}

function getBoundaryBoxCenter() {
    let boundingBox = $("#BoundaryBox")[0];
    let offsetTop = boundingBox.offsetTop;
    let offsetLeft = boundingBox.offsetLeft;
    let height = boundingBox.clientHeight;
    let width = boundingBox.clientWidth;
    let center = {x: (offsetLeft + width / 2), y: (offsetTop + height / 2)};
    return center;
}

function toggleProgress(off) {
    if (!off && $("#ProgressOn").css("display") === "none") {
        $("#ProgressOff").css("display", "none");
        $("#ProgressOn").css("display", "grid");
    } else {
        $("#ProgressOff").css("display", "grid");
        $("#ProgressOn").css("display", "none");
    }
}

function toggleLibrary(button) {
    if (map.getLayer('drawings')) {
        button.innerText = "Library";
        removeLibrary();
    } else {
        button.innerText = "Hide";
        drawLibrary();
    }
}

function removeLibrary() {
    map.removeLayer('drawings');
    map.removeLayer('borders');
}

function drawLibrary() {
    if (map.getSource('drawings')) {
        map.addLayer({
            'id': 'drawings',
            'type': 'fill',
            'source': 'drawings',
            'layout': {},
            'paint': {
                'fill-outline-color': '#649aff',
                'fill-color': '#74aaff',
                'fill-opacity': 0.1,
            }
        });
        map.addLayer({
            'id': 'borders',
            'type': 'line',
            'source': 'drawings',
            'layout': {},
            'paint': {
                'line-color': '#649aff',
                'line-opacity': 0.8,
                'line-width': 2,
            }
        });
    } else {
        const xhr = new XMLHttpRequest();
        const uri = encodeURI(hostUrl() + 'drawings');
        xhr.open("GET", uri, true);
        xhr.onload = () => {
            let response = JSON.parse(xhr.responseText);
            console.log(response);
            map.addSource('drawings', {type: 'geojson', data: response});
            map.addLayer({
                'id': 'drawings',
                'type': 'fill',
                'source': 'drawings',
                'layout': {},
                'paint': {
                    'fill-outline-color': '#649aff',
                    'fill-color': '#74aaff',
                    'fill-opacity': 0.1,
                }
            });
            map.addLayer({
                'id': 'borders',
                'type': 'line',
                'source': 'drawings',
                'layout': {},
                'paint': {
                    'line-color': '#649aff',
                    'line-opacity': 0.8,
                    'line-width': 2,
                }
            });
        }
        xhr.send();
    }
}

function removeContours() {
    map.removeLayer('land');
    map.removeLayer('depths');
    map.removeLayer('contours');
    if (map.getLayer('selected')) {
        map.removeLayer('selected');
    }
}

function deleteContours() {
    if (map.getLayer('contours')) {
        removeContours();
    }
    if (map.getSource('contours')) {
        map.removeSource('land');
        map.removeSource('contours');
    }
}

function drawContours(leadHash) {
    if (map.getSource('contours')) {
        map.addLayer({
            'id': 'contours',
            'type': 'line',
            'source': 'contours',
            'layout': {},
            'paint': {
                'line-color': '#088',
                'line-opacity': 0.8
            }
        });
        map.addLayer({
            'id': 'depths',
            'type': 'fill',
            'source': 'contours',
            'layout': {},
            'paint': {
                'fill-color': '#0aa',
                'fill-opacity': 0.0
            }
        });
        map.addLayer({
            'id': 'land',
            'type': 'fill',
            'source': 'land',
            'layout': {},
            'paint': {
                'fill-color': '#54aa30',
                'fill-opacity': 0.8
            }
        });
    } else {
        let req = new XMLHttpRequest();
        req.open('GET', 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + leadHash + '/contours.geojson');
        req.send();
        req.onreadystatechange = () => {
            if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
                let geojson = JSON.parse(req.response);
                geojson.features.sort((a, b) => {
                    const a_ = a.properties.elevation;
                    const b_ = b.properties.elevation;
                    if (a_ === b_) {
                        return 0
                    } else if (a_ < b_) {
                        return -1
                    } else {
                        return 1
                    }
                })
                map.addSource('contours', {
                    'type': 'geojson',
                    'data': geojson
                });
                map.addLayer({
                    'id': 'contours',
                    'type': 'line',
                    'source': 'contours',
                    'layout': {},
                    'paint': {
                        'line-color': '#088',
                        'line-opacity': 0.8
                    }
                });
                map.addLayer({
                    'id': 'depths',
                    'type': 'fill',
                    'source': 'contours',
                    'layout': {},
                    'paint': {
                        'fill-color': '#0aa',
                        'fill-opacity': 0.0
                    }
                });

                map.addSource('land', {
                    'type': 'geojson',
                    'data': 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + leadHash + '/land.geojson'
                });

                map.addLayer({
                    'id': 'land',
                    'type': 'fill',
                    'source': 'land',
                    'layout': {},
                    'paint': {
                        'fill-color': '#54aa30',
                        'fill-opacity': 0.8
                    }
                });
            }
        }
    }
}

function nextLead() {
    let len;
    if (unread) {
        len = Object.keys(leads[leadType]).length;
    } else {
        len = pending[leadType].length;
    }
    console.log('current lead:' + leadId)
    leadId += 1;
    console.log('changing to lead:' + leadId)
    if (leadId < len) {
        leadIndex = 0;
        selectLead();
    } else {
        let typeKey = {
            New: "Quoted",
            Quoted: "Design",
            Design: "Invoice",
            Invoice: "Production",
            Production: "Other",
        }
        if (typeKey[leadType]) {
            getLeadType(typeKey[leadType]);
        } else {
            window.location.reload(true);
        }
    }
}

function previousLead() {
    leadId = (leadId == 0 ? 1 : leadId) - 1;
    leadIndex = 0;
    selectLead();
}

function getLeadType(type) {
    unread = true;
    $("#" + leadType + "Pending").css("color", '');
    $("#" + leadType).css("color", '');
    leadType = type;
    leadId = 0;
    leadIndex = 0;
    $("#" + leadType).css("color", "#cfb28a");
    selectLead();
}

function getPending(type) {
    unread = false;
    $("#" + leadType + "Pending").css("color", '');
    $("#" + leadType).css("color", '');
    leadType = type;
    leadId = 0;
    leadIndex = 0;
    $("#" + leadType + "Pending").css("color", "#cfb28a");
    selectLead();
}


function hideCancelButtons() {
    let cancelButtons = $(".LeadCancel");
    for (let i = 0; i < cancelButtons.length; i++) {
        cancelButtons[i].style.display = 'none';
    }
}

function uploadDesign(file) {
    console.log(file);
    let req = new XMLHttpRequest();
    let formData = new FormData();
    let url = hostUrl() + 'render/' + activeLead.id;

    formData.append("file", file);
    req.open("POST", url);
    req.onreadystatechange = () => {
        if (req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            console.log('Lead render updated')
            nextLead();
        }
    };
    req.send(formData);
}

map.on('click', 'drawings', (e) => {
    let coordinates = {lat: e.features[0].properties.lat, lng: e.features[0].properties.lng};
    let key = e.features[0].properties.key;
    let count = e.features[0].properties.count;
    let image = e.features[0].properties.image;
    new mapboxgl.Popup()
        .setLngLat(coordinates)
        .setHTML("<a href='?count=" + count + "'>" + key + "</a>")
        .addTo(map);
    $("#DataBox")[0].src = image;
})

map.on('click', 'depths', (e) => {
    if (map.getSource('contours')) {
        const depth = e.features[0].properties.elevation;
        new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(depth.toFixed(2) + 'm')
            .addTo(map);
        if (map.getLayer('selected')) {
            map.removeLayer('selected');
        }
        // TODO: set line style,
        //      add to contour list
        //      cap at 7
        //      remove if already in list
        //      order contours highest to lowest
        map.addLayer({
            "id": "selected",
            "type": "fill",
            "source": "contours",
            "layout": {},
            'paint': {
                'fill-color': '#ffffff',
                'fill-opacity': 0.8
            },
            "filter": ["==", "elevation", depth]
        });
    }
})

map.on('load', () => {
    let bodyResize = new ResizeObserver(mapResize).observe($("#parent")[0]);
    getLeads();
})

$(document).ready(() => {

    $("#BoundaryBox").mouseover(() => {
        $("#map").css("pointerEvents", "all");
        $("#BoundaryBox").css("pointerEvents", "none");
    });

    $("#map").mouseout(() => {
        $("#map").css("pointerEvents", "none");
        $("#BoundaryBox").css("pointerEvents", "all");
    });

    let sizeOptions = $("#LeadSize");
    sizeOptions.focus(() => {
        sizeOptions.val('');
    });
    sizeOptions.blur(() => {
        let map_units = $("#Metric").val() ? "mm" : '"';
        $("#LeadDescription").val('Map Size: ' + $("#LeadSizeOptions").find('option[value="' + sizeOptions.val() + '"]').text() + map_units + ' + FREE Wooden Gift Box');
    });

    $("#Id").blur(getLeadId);

    $("#Email").blur(getLeadEmail);

    $("#IdDetail").blur(getLeadId);

    $("#EmailDetail").blur(getLeadEmailDetail);

    $("#LibraryButton").click(() => {
        toggleLibrary($("#LibraryButton")[0])
    });

    $("#BoundaryButton").click(() => {
        setStatus(110)
    });

    $("#QuotedButton").click(() => {
        setStatus(210)
    });

    $("#DesignButton").click(() => {
        setStatus(310)
    });

    $("#InvoiceButton").click(() => {
        setStatus(410)
    });

    $("#PaidButton").click(() => {
        setStatus(500)
    });

    $("#ProductionButton").click(() => {
        setStatus(600)
    });

    $("#BadEmail").click(() => {
        setStatus(900, true);
        hideCancelButtons();
    });

    $("#ReadEmail").click(() => {
        markRead();
        hideCancelButtons();
        nextLead();
    });

    $("#Landscape").click(() => {
        setStatus(901, true);
        hideCancelButtons();
    });

    $("#BadDesign").click(() => {
        setStatus(902, true);
        hideCancelButtons();
    });

    $("#TooExxy").click(() => {
        setStatus(903, true);
        hideCancelButtons();
    });

    $("#NotInterested").click(() => {
        setStatus(904, true);
        hideCancelButtons();
    });

    $("#Hold").click(() => {
        setStatus(905, true);
        hideCancelButtons();
    });

    $("#LongHold").click(() => {
        setStatus(906, true);
        hideCancelButtons();
    });

    $("#NoData").click(() => {
        setStatus(920, true);
        hideCancelButtons();
    });

    $("#CancelButton").click(() => {
        let top = $("#CancelButton").offset().top + 65;
        let left = $("#CancelButton").offset().left + 40;
        let buttonHeight = 40;
        let cancelButtons = $(".LeadCancel");
        if (cancelButtons[0].style.display === 'block') {
            hideCancelButtons();
        } else {
            for (let i = 0; i < cancelButtons.length; i++) {
                cancelButtons[i].style.display = 'block';
                cancelButtons[i].style.left = left + 'px';
                cancelButtons[i].style.top = (top + (i * buttonHeight)) + 'px';
            }
            window.setTimeout(() => {
                hideCancelButtons();
            }, 10 * 1000);
        }
    });

    $("#Metric").click(() => {
        $("#UnitsRadioButton")[0].children[0].checked = true;
        if ($("#Metric").val()) {
            $("#Metric").val(false);
            $("#Metric").css("color", "#897a51");
            $("#Imperial").css("color", "#fafafa");
            setSizes('imperial');
        } else {
            $("#Metric").val(true);
            $("#Metric").css("color", "#fafafa");
            $("#Imperial").css("color", "#897a51");
            setSizes('metric');
        }
    });

    $("#Imperial").click(() => {
        $("#UnitsRadioButton")[0].children[0].checked = true;
        if (!$("#Metric").val()) {
            $("#Metric").val(true);
            $("#Imperial").css("color", "#897a51");
            $("#Metric").css("color", "#fafafa");
            setSizes('metric');
        } else {
            $("#Metric").val(false);
            $("#Imperial").css("color", "#fafafa");
            $("#Metric").css("color", "#897a51");
            setSizes('imperial');
        }
    });

    $("#Render").click(() => {
        $("#RenderRadioButton")[0].children[0].checked = true;
        if ($("#Render").val()) {
            $("#Render").val(false);
            $("#Render").css("color", "#897a51");
            $("#Logo").css("color", "#fafafa");
        } else {
            $("#Render").val(true);
            $("#Render").css("color", "#fafafa");
            $("#Logo").css("color", "#897a51");
        }
    });

    $("#Logo").click(() => {
        $("#RenderRadioButton")[0].children[0].checked = true;
        if (!$("#Render").val()) {
            $("#Render").val(true);
            $("#Logo").css("color", "#897a51");
            $("#Render").css("color", "#fafafa");
        } else {
            $("#Render").val(false);
            $("#Logo").css("color", "#fafafa");
            $("#Render").css("color", "#897a51");
        }
    });

    $("#MarkButton").click(() => {
        let bb = $("#BoundaryBox")[0];
        let p1 = {x: bb.offset().left, y: bb.offset().top};
        let p2 = {x: p1.x + bb.width(), y: p1.y + bb.height()};
        let pxy = map.project(marker.getLngLat());
        if (pxy.x > p1.x && pxy.x < p2.x && pxy.y > p1.y && pxy.y < p2.y) {
            marker.setLngLat([0, 0]);
            marker.remove();
            $("#LeadMark").val('0.0, 0.0');
        } else {
            marker.addTo(map);
            marker.setLngLat(map.getCenter());
            $("#LeadMark").val(map.getCenter().lat.toFixed(4) + ', ' + map.getCenter().lng.toFixed(4));
        }
    });

    $("#RefreshBoundary").click(updateBoundary);

    $("#SaveLeadDetailsButton").click(updateLead);

    $("#ProgressButton").click(() => {
        toggleProgress()
    });

    $("#SpecialButton").click(() => {
        setStatus(666)
    });

    $("#UploadButton").click(() => {
        let fileSelector = $('<input>');
        fileSelector[0].setAttribute('type', 'file');
        fileSelector.change(() => {
            uploadDesign(fileSelector[0].files[0]);
        });
        fileSelector[0].click();
    });

    $("#CreateInvoiceButton").click(() => {
        updateLead(() => {
            let invoiceURL = hostUrl() + 'xero/?lead=' + activeLead.id;
            window.open(invoiceURL);
        })
    });

    let designs = $(".DesignButton");
    let designNames = $(".radioText");
    for (let i = 0; i < designs.length; i++) {
        let design = designs[i];
        design.onclick = () => {
            let index = design.value;
            $("#DesignText")[0].innerText = designNames[i].innerText;
            if (index == '0') {
                index = '';
            }
            $("#DesignBox")[0].src = 'https://pangea-render-data.s3-ap-southeast-2.amazonaws.com/' + activeLead.hash + '/' + activeLead.map + index + '_canvas.png';
        }
    }

    let leadDetails = $(".DetailText");
    for (let i = 0; i < leadDetails.length; i++) {
        leadDetails[i].onchange = () => {
            leadDetails[i].parentNode.parentNode.getElementsByClassName("UpdateCheck")[0].checked = true;
            if (leadDetails[i].id === "LeadPrice" && +leadDetails[i].value > 5000) {
                alert('Double check Price: ' + leadDetails[i].value)
            }
            if (leadDetails[i].id === "LeadInvoice" && (+leadDetails[i].value > 10000 || +leadDetails[i].value < 5000)) {
                alert('Double check invoice number: ' + leadDetails[i].value)
            }
        };
    }
})