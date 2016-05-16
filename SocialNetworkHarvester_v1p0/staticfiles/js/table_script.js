$.getScript("/static/js/DataTables-1.10.9/js/jquery.dataTables.min.js")
$.getScript("/static/js/Select-1.0.1/js/dataTables.select.min.js")
$.getScript("/static/js/linkify/linkify.min.js", function(){
    $.getScript("/static/js/linkify/linkify-string.min.js")
})


var selectedTableRows = [];
var maxSelecteditems = 1000;
function maxSelectionCallback(){alert("You can only select "+maxSelecteditems+" items at a time!");}

var default_asSorting = ["desc", "asc", "none"];

$(document).ready(function() {

    $(".section_title").click(function(){
        var content = $(this).parent().next(".section_content");
        var options = $(this).next(".section_options");
        var table = content.children();
        if(options.length != 0){
            menuToggle(options);
        }
        if(content.length != 0){
            content.slideToggle(300);
            if (table.attr('drawn') == 'False'){
                drawTable(table);
            }
        }
        //log($(this).parent().children(".tableOpenCloseIcon"))
        togglePlusMinusSign($(this).parent().children(".tableOpenCloseIcon"))
    });

    $('.tableOpenCloseIcon').click(function(){
        var content = $(this).parent().next(".section_content");
        var options = $(this).prev(".section_options");
        var table = content.children();
        if(options.length != 0){
            menuToggle(options);
        }
        if(content.length != 0){
            content.slideToggle(300);
            if (table.attr('drawn') == 'False'){
                drawTable(table);
            }
        }
        togglePlusMinusSign($(this));
    });

    $('.table_select_master').each(function(){
        $(this).prop('checked', false) ;
    }).click(function(){
        var table = $(this).parents('.display');
        setProcessing(table, true);
        var fullURL = table.DataTable().ajax.json()['fullURL']
        var modifiedURL = fullURL.replace(/iDisplayStart=[0-9]*/, 'iDisplayStart=0');
        var modifiedURL = modifiedURL.replace(/iDisplayLength=[0-9]*/, 'iDisplayLength='+(maxSelecteditems+1));
        if($(this).prop('checked')){
            $.ajax({"url":modifiedURL,
                "success": function(data){
                    data.data.some(function(item){
                        if (selectedTableRows.length < maxSelecteditems){
                            pushUniqueIn(selectedTableRows, item['DT_RowId']);
                        } else {
                            maxSelectionCallback()
                            return true;
                        }
                    });
                    table.find('tr').each(function(){
                        $(this).addClass('selected');
                    });
                    setProcessing(table, false);
                    $('body').trigger('selectedTableRowsChanged');
                }
            })
        } else {
            $.ajax({"url":modifiedURL,
                "success": function(data){
                    data.data.forEach(function(item){
                        removeFrom(selectedTableRows, item['DT_RowId']);
                    });
                    table.find('tr').each(function(){
                        $(this).removeClass('selected');
                    });
                    setProcessing(table, false);
                    $('body').trigger('selectedTableRowsChanged');
                }
            })
        }
    });

    $('[id="reloadTableLink"]').click(function(){
        var content = $(this).parent().parent().next(".section_content");
        var table = content.children().children("table");
        var scriptTag = table.children('.tableVars');
        var dynamicSource=false;
        var GETValues=null;
        eval(scriptTag.text())
        var source = url+"?fields="+fields;
        if (dynamicSource) {
            source += getSourcesFromSelectedRows();
        }
        if (GETValues != null){
            source += obtainGETValues(GETValues);
        }
        table.DataTable().ajax.url(source);
        table.DataTable().ajax.reload();
    });
    $("body").on('mouseover', '.snippetHover', function(event){
        if($('#snippetContainer').length == 0) {
            var href = $(this).attr('href') + "?snippet=true";
            var snippet = "<div id='snippetContainer'>" +
                "<iframe id='snippet' scrolling='no' src="+href+"/>" +
                "</div>"
            $("body").append(snippet);
            $('#snippetContainer').position({
                my: "left+10 top",
                of: event,
                collision: "fit",
                within:$("#content_container")
            })
            tmOutFcn = setTimeout(function () {
                $('#snippet').css('display', 'block')
            }, 1500);
        }
    });
    $("body").on('mouseout', '.snippetHover',function(){
        clearTimeout(tmOutFcn);
        $('#snippetContainer').remove();
    });

    $(".option_checkbox").each(function(){
        $(this).prop('checked', false) ;
    }).click(function() {
        var content = $(this).closest(".section_menu").next(".section_content");
        var table = content.children().children("table");
        var scriptTag = table.children('.tableVars');
        var dynamicSource=false;
        var GETValues=null;
        eval(scriptTag.text())
        var source = url+"?fields="+fields;
        if (dynamicSource) {
            source += getSourcesFromSelectedRows();
        }
        if (GETValues != null){
            source += obtainGETValues(GETValues);
        }
        if ($(this).prop('checked')){
            source += "&"+$(this).attr('name')+"=true";
        }
        table.DataTable().ajax.url(source);
        table.DataTable().ajax.reload();
    });
});

function togglePlusMinusSign(sign){
    var src = sign.children('img').attr('src')
    if(sign.attr('type') == 'plus') {
        src = src.replace(/\/[^\/]+\.png/, '/minus_icon_128.png')
        sign.attr('type', 'minus');
    } else if (sign.attr('type') == 'minus'){
        src = src.replace(/\/[^\/]+\.png/, '/plus_icon_128.png')
        sign.attr('type', 'plus');
    }
    sign.children('img').attr('src', src)
}

function obtainGETValues(GETValues){
    var ret = "";
    GETValues.forEach(function(entry){
        ret += "&"+entry;
    });
    return ret;
}

function setProcessing(table, value){
    var oSettings = null;
    table.dataTable().dataTableSettings.some(function(o){
        if (o.nTable.id == $(table).attr('id')){
            oSettings = o;
            return true;
        }
    })
    table.dataTable().oApi._fnProcessingDisplay(oSettings, value);
}

function drawTable(table){
    var language = {
        "processing": "Working on it...",
        "thousands":",",
    };
    var languageParams = {};
    var scriptTag = table.children('.tableVars');
    var dynamicSource=false;
    var GETValues=null;
    eval(scriptTag.text());
    var source = url+"?fields="+fields;
    if (dynamicSource) {
        source += getSourcesFromSelectedRows();
    }
    if (GETValues != null){
        source += obtainGETValues(GETValues);
    }
    if (languageParams){
        for(var param in languageParams){
            language[param] = languageParams[param];
        }
    }
    //log(source)
    $.fn.dataTable.ext.errMode = 'throw';
    table.DataTable({
        "iDisplayLength": 10,
        "autoWidth": false,
        "serverSide": true,
        "sAjaxSource": source,
        "columnDefs": columnsDefs,
        "language": language,
        "processing": true,
        "rowCallback": function( row, data ) {
            if ( $.inArray(data.DT_RowId, selectedTableRows) !== -1 ) {
                $(row).addClass('selected');
            }
        }
    });
    disableLiveInputSearch();
    customSelectCheckbox(table);
    table.attr('drawn', 'True');
}

function disableLiveInputSearch(){
    $("div.dataTables_filter input").unbind()
    .keyup( function (e) {
        if (e.keyCode == 13) {
            var table = $(this).parent().parent().parent().children('table')
            table.dataTable().fnFilter(this.value);
        }
    });
}

function customSelectCheckbox(table){
    table.on('click', 'td.select-checkbox', function () {
        var id = $(this).parent().attr('id');
        if (!$(this).parent().hasClass('selected')){
            if (selectedTableRows.length < maxSelecteditems){
                pushUniqueIn(selectedTableRows, id);
                $(this).parent().addClass('selected');
            } else {maxSelectionCallback();}
        } else {
            removeFrom(selectedTableRows, id);
            $(this).parent().removeClass('selected');
        }
        $('body').trigger('selectedTableRowsChanged');
    });
}

function pushUniqueIn(array, item){
    var index = $.inArray(item, array);
    if (index === -1) {
        array.push(item);
    }
}

function removeFrom(array, item){
    var index = $.inArray(item, array);
    if (index != -1) {
        array.splice(index, 1);
    }
}

function toggleFrom(array, id){
    var index = $.inArray(id, array);
    if (index === -1) {
        array.push(id);
    } else {
        array.splice(index,1);
    }
}

function menuToggle(elem){
    if (elem.css('width') == '0px'){
        elem.animate({
            width: parseInt(elem.parent().css("width")) - parseInt(elem.prev(".section_title").css("width"))-35
        },300);
    } else {
        elem.animate({width:0},300);
    }
}

function getSourcesFromSelectedRows(){
    var sources = "";
    for (var i = 0; i<selectedTableRows.length; i++){
        sources += selectedTableRows[i]+",";
    }
    return "&selected_rows="+sources;
}

function formatTweetText(text){
    text = linkifyStr(text, {linkClass :"TableToolLink"})

    log(text);
    var userRegex = /@([A-Z]|[0-9]|_)+/ig;
    var usernames = text.match(userRegex);
    if (usernames != null) {
        usernames.forEach(function (username) {
            log(username);
            text = text.replace(username, '<a class="TableToolLink snippetHover" target="_blank" href="/twitter/user/' + username.slice(1) + '">' + username + '</a>');
        });
    }

    var hashtagRegex = /#([A-Z]|[0-9]|_)+/ig;
    var hashtags = text.match(hashtagRegex);
    if (hashtags != null) {
        hashtags.forEach(function (hashtag) {
            log(hashtag);
            text = text.replace(hashtag, '<a class="TableToolLink" target="_blank" href="/twitter/hashtag/' + hashtag.slice(1) + '">' + hashtag + '</a>');
        });
    }

    return text;
}