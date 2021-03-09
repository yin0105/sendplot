###
#
###

refresh_delay = 10000
drawing_json = undefined
drawings = {}
search_strings = []
sorted_printers = []
default_printer = 'ISLaserBsize'
selected_el = undefined
previous_button = false
action_links = {}
show_more_menu = false
printers_json = undefined
is_summary = 'True'
more_btn_background = '#FFF'
more_btn_color = 'rgb(85, 85, 255)'

###*************************************************************************************************
#                            Click on more info button
*************************************************************************************************
###

###*************************************************************************************************
#                            Update list of drawings
*************************************************************************************************
###

update_list = ->
  #summary = get_summary()
  $('#list_queue').empty()
  drawings = {}
  $('#notes').hide()
  $('#misplaced_files').hide()
  $('#info').html ''
  if is_summary
    more_btn_background = '#eee'
    more_btn_color = '#ccc'
  else
    more_btn_background = '#fff'
    more_btn_color = 'rgb(85, 85, 255)'

  $('#More_btn').css
    'background-color': more_btn_background
    'color': more_btn_color
  $('#search').val $('#search').val().toUpperCase()
  search_strings = $('#search').val().split(' ')
  ajaxCallsRemaining = search_strings.length
  # *********  Check for empty search box
  if $.trim(search_strings[0]) == ''
    $('#search').val 'Search for stuff'
    return
  $.each search_strings, (search_index) ->
    drawing_json = $.ajax(
      dataType: 'json'
      url: '/api/search/' + search_strings[search_index]).done((drawing_json) ->
      # console.log(drawing_json);
      # drawing_json = fix_search_results(drawing_json);
      # console.log(drawing_json);
      if drawing_json.results == 'no files found'
        $('#flash').html 'no files found'
        flash_message()
        $('#search').select()
        return
      #console.log('*** drawing_json: ', drawing_json)
      #console.log('*** is_summary: ', (is_summary == true))
      if is_summary
        drawings[search_strings[search_index]] = filter_drawings(search_strings[search_index], drawing_json)
        #console.log('*** drawings: ', drawings[search_strings[search_index]])
      else
        drawings[search_strings[search_index]] = drawing_json

      drawing_json = drawings[search_strings[search_index]]
      previous_button = false
      sorted = []
      for key of drawing_json
        sorted[sorted.length] = key
      sorted.sort()
      yogi = '<br><br> If you don\'t know where you\'re going...<br>
              ...you might not get there...<br>
              - <a href="http://en.wikipedia.org/wiki/Yogi_Berra" target="_blank"> Yogi Berra </a>'
      $.each sorted, (index) ->
        if drawing_json[sorted[index]] != 'stats'
          #var key = sorted[index];
          $('#list_queue').append '<li class="list-group-item pdf" id="' + sorted[index] + '">' + sorted[index] + '</li>'
        return
      $('#list').scrollTop 0
      count = Object.keys(drawing_json).length
      $('#list_drawings').empty()
      if count > 1000
        $('#returned_count').html 'More than 1000 items -- please narrow your search. '
        $('#flash').html 'Search returned too many results...' + yogi
        $('#returned_count').addClass 'alert alert-warning'
        $('#returned_count').removeClass 'alert alert-info'
        flash_message()
      else
        $('#returned_count').html count + ' items returned'
        $('#returned_count').addClass 'alert alert-info'
        $('#returned_count').removeClass 'alert alert-warning'
      $('#returned_count').delay(300).fadeIn 'normal', ->
        $(this).delay(2000).fadeOut()
        return
      $('#submit').focus()
      --ajaxCallsRemaining
      # console.log('search len: ' + search_strings.length, 'index: ' + search_index);
      if ajaxCallsRemaining <= 0
        # console.log('triggered');
        selected_el = $('ul#list_queue li:first')
        $('ul#list_queue li:first').trigger 'click'
      return
    )
    return
  return

###*************************************************************************************************
#                            Remove spaces from returned search keys
*************************************************************************************************
###

fix_search_results = (drawing_json) ->
  # console.log('json len: ', Object.keys(drawing_json).length);
  for key of drawing_json
    if key.indexOf(' ')
      fixed_key = key.replace(/\ /g, '_')
      # fixed_key = key.replace(/[^a-zA-Z0-9]/g,'_');
      drawing_json[fixed_key] = drawing_json[key]
      delete drawing_json[key]
  drawing_json

###*************************************************************************************************
#                            Filter drawings - print only
*************************************************************************************************
###

filter_drawings = (search_item, drawings) ->
  ret_drawings = {}
  #console.log('search item: ', search_item)
  #console.log('drawings: ', drawings)
  $.each drawings, (drawing) ->
    #console.log('drawing: ', drawing)
    print_drawings = []
    $.each drawings[drawing], (item) ->
      if drawings[drawing][item].indexOf('pdf_out') > -1 || drawings[drawing][item].indexOf('mb-archive') > -1
        #console.log('item: ', drawings[drawing][item])
        print_drawings.push(drawings[drawing][item])
    #console.log('prints: ', print_drawings.length)
    if print_drawings.length > 0
      ret_drawings[drawing] = print_drawings

  #console.log('ret_drawings: ', ret_drawings)
  #console.log('ret_drawings.length: ', Object.keys(ret_drawings).length)
  #if Object.keys(ret_drawings).length > 0
    #ret_searches[search_item] = ret_drawings
  return ret_drawings

  #console.log('ret_searches: ', ret_searches)
  #return ret_searches


###*************************************************************************************************
#                            Flash message on web page
*************************************************************************************************
###

flash_message = ->
  $ ->
    $('#flash').delay(300).fadeIn 'normal', ->
      $(this).delay(3500).fadeOut()
      return
    return
  return

###*************************************************************************************************
#                            Click on search result
*************************************************************************************************
###

getFirstKey = (data) ->
  for elem of data
    return elem
  return

handle_results_clicks = ($el) ->
  $('.active').removeClass 'active'
  $('#info').html ''
  $('#notes').hide()
  $('#menu_more').empty()
  # console.log('click pdf', $el.id);
  if previous_button != $(this).attr('id')
    $('#menu_more').hide()
    show_more_menu = false
  items = ''
  val = undefined
  action_btns = {}
  drawing_name = $el.id
  if $('#' + drawing_name).length == 0
    return
  if previous_button and $('#' + previous_button)[0]
    $('#' + previous_button)[0].innerHTML = previous_button
  previous_button = drawing_name
  $('#list_drawings').empty()
  # console.log('handle - search len: ' + search_strings.length, search_strings[0], search_strings[1], search_strings[2]);
  sString = undefined
  # console.log( ' *******' );
  $.each search_strings, (index) ->
    if typeof drawings[search_strings[index]] != 'undefined'
      sString = search_strings[index].toUpperCase()
      drawing_name = drawing_name.toUpperCase()
      # console.log( ' ** search string:', sString );
      if search_strings.length > 1
        # val = getFirstKey( drawings[search_strings[index]] );
        if drawing_name.indexOf(sString) != -1
          # console.log('match search string', sString, drawing_name, drawing_name.indexOf(sString), drawings);
          val = drawings[sString][drawing_name]
          # console.log('index: ', index,  drawings, search_strings[index], 'drawings: ',  drawings[sString][drawing_name], val  );
        else
          # console.log('no match search string', sString, drawing_name );
        # console.log( 'first key:', index, getFirstKey( drawings[search_strings[index]] ));
      else
        val = drawings[sString][drawing_name]
    return
  # ******************************* buttons in reverse order in order to float right
  action_btns.More = 'disabled'
  action_btns.PDF = 'disabled'
  action_btns.Print = 'disabled'
  action_btns.Delete = 'disabled'
  action_links = {}
  # console.log( 'val', val, drawing_name, drawings, drawings[drawing_name] );
  $.each val, (item) ->
    s = val[item]
    drawing_link = val[item]
    more_info_link = ''
    data_id = drawing_name
    if drawing_link.indexOf('/imported/') > -1
      info_button = '<a id="more_info" data-id="' + data_id + '">Linked data</a>'
      more_info_link = '&nbsp;&nbsp;' + info_button
      action_btns.More = 'enabled'
      action_links['More info'] = data_id
      $('#menu_more').append '<li class="list-group-item">' + more_info_link + '</li>'
    else if drawing_link.indexOf('mb-archive') > -1
      mb_drawings_button = '<a id="mb_drawing_list" data-id="' + data_id + '">MB Drawing List</a>'
      more_info_link = '&nbsp;&nbsp;' + mb_drawings_button
      action_btns.More = 'enabled'
      action_links['MB Drawing List'] = data_id
      $('#menu_more').append '<li class="list-group-item">' + more_info_link + '</li>'
      #media_button = '<a id="media_list" data-id="' + data_id + '">Media List</a>'
      #$('#menu_more').append '<li class="list-group-item">&nbsp;&nbsp;' + media_button + '</li>'
      #
    if drawing_link.toUpperCase().lastIndexOf('.PRF') > 0
      action_links.PRF = drawing_link
      # $('#list_drawings').append '<li class="list-group-item">' + plot_menu('PRF', drawing_link) + '</li>'
      action_btns.Print = 'enabled'
    else if drawing_link.toUpperCase().lastIndexOf('.PDF') > 0
      action_links.PDF = drawing_link
      action_links.PRF = drawing_link
      pdf_modified = get_file_meta(drawing_link)
      # $('#list_drawings').append( '<li class="list-group-item">' + plot_menu('PDF', drawing_link) +'</li>'); 
      $('#list_drawings').append '<li class="list-group-item"><a href="' + drawing_link + '" title="  ' + drawing_link + '  " target="_blank">' + s.substring(s.lastIndexOf('/') + 1) + '  </a>' + more_info_link + '</li>'
      action_btns.PDF = 'enabled'
      action_btns.Print = 'enabled'
    else
      s_type = drawing_link.substring(drawing_link.lastIndexOf('.') + 1)
      action_links[s_type] = drawing_link
      $('#list_drawings').append '<li class="list-group-item"><a href="' + drawing_link + '" title="  ' + drawing_link + '  " target="_blank">' + s.substring(s.lastIndexOf('/') + 1) + '  </a>' + more_info_link + '</li>'
      $('#menu_more').append '<li class="list-group-item"><a href="#" class="download_file" data-id="' + drawing_link + '" title="   ' + drawing_link + '   " >' + s.substring(s.lastIndexOf('/') + 1) + '  </a>' + more_info_link + '</li>'
      action_btns.More = 'enabled'
    return
  # console.log('#' + drawing_name);
  if $('#' + drawing_name)[0]
    $('#' + drawing_name)[0].className = 'list-group-item pdf active'
  # **************************************** build context buttons
  s_buttons = ''
  for key of action_btns
    s_disabled = ''
    if action_btns[key] == 'disabled'
      s_disabled = ' disabled="disabled" class="btn_actions btn_disabled"'
    else
      s_disabled = ' class="btn_actions"'
    s_buttons += '<button type="button" id="' + key + '_btn" ' + s_disabled + ' data-id="' + drawing_name + '"> ' + key + ' </button>'
  if $('#' + drawing_name)[0]
    $('#' + drawing_name)[0].innerHTML = drawing_name + s_buttons
  if action_btns.Print == 'disabled'
    $('#Print_btn').addClass 'print_btn_disabled'
  else
    $('#Print_btn').addClass 'print_btn'
  $('#btn_pdf').attr 'disabled', 'disabled'
  $('#More_btn').html $('#More_btn').html()
  return

###*************************************************************************************************
#                            Click on action buttons
*************************************************************************************************
###

handle_action_clicks = ($el) ->
  # console.log('click action: ',  $el.id);
  $('#menu_more').hide()
  switch $el.id
    when 'Print_btn'
      if default_printer == 'no cookie'
        $('#flash').html 'No Printer Selected!<br><br>To print, click <strong>Printers</strong> above and select a printer.'
        flash_message()
        return
      $.ajax(url: '/print/' + default_printer + action_links.PRF.substring(action_links.PRF.indexOf('/', 2)))
        .done (data) ->
          #console.log('print data:', data)
          $('#flash').html action_links.PRF.substring(action_links.PRF.lastIndexOf('/') + 1, action_links.PRF.lastIndexOf('.')) + ' printed on ' + printers_json.responseJSON[default_printer] + '<br>(click Printers menu to change)'
          $('#returned_count').addClass 'alert alert-info'
          flash_message()
          # console.log('plot_prf/' + default_printer  + action_links.PRF + '\"); return false;\' >');
          return
        .fail (data) ->
          #console.log('print data:', data)
          #console.log('print result:', JSON.parse(data.responseText)['action'])
          $('#flash').html JSON.parse(data.responseText)['action'] + '<br><br>Report missing file to Engineering or I.S.'
          flash_message()
          return
    when 'PDF_btn'
      # console.log(action_links.PDF);
      window.open action_links.PDF, '_blank', ''
      # console.log(action_links.PDF);
      $('#flash').html action_links.PDF.substring(action_links.PDF.lastIndexOf('/') + 1) + ' downloaded'
      $('#returned_count').addClass 'alert alert-info'
      $('#notes').hide()
      flash_message()
    when 'More_btn'
      # console.log(action_links);
      # get_more_menu();
      if show_more_menu
        $('#menu_more').hide()
        $('#More_btn').css
          'background-color': more_btn_background
          'color': more_btn_color
        show_more_menu = false
      else
        show_more_menu = true
        get_more_menu()
        # $('#More_btn').css({ 'background-color': '#f00', 'color': '#fff' });
        $('#More_btn').css
          'background-color': '#f00'
          'color': '#fff'
          'background': 'red'
        # console.log('set background');
  # console.log('done action: ', $el.id);
  return

download_file = (drawing_link) ->
  file_return = $.ajax(
    dataType: 'json'
    url: drawing_link).always((data) ->
    if typeof file_return.responseJSON != 'undefined'
      first_pos = drawing_link.indexOf('/', 1) + 1
      second_pos = drawing_link.lastIndexOf('/')
      missing_file = ' / ' + drawing_link.substring(first_pos, second_pos) + ' / ' + drawing_link.substring(drawing_link.lastIndexOf('/') + 1)
      $('#flash').html file_return.responseJSON.results + '<br>[ ' + missing_file + ' ]'
      $('#returned_count').addClass 'alert alert-info'
      flash_message()
    else
      window.open drawing_link, '_blank'
      downloaded_file = drawing_link.substring(drawing_link.lastIndexOf('/') + 1)
      $('#flash').html 'File downloaded.<br>[' + downloaded_file + ']'
      $('#returned_count').addClass 'alert'
      flash_message()
    return true
  )
  return true

get_file_meta = (drawing_link) ->
  file_url = drawing_link.substring(1, drawing_link.lastIndexOf('/'))
  file_name = drawing_link.substring(drawing_link.lastIndexOf('/') + 1)
  # console.log(file_url, file_name, file_url.substring(file_url.lastIndexOf('/') + 1));
  file_meta = $.ajax(
    url: '/api/get_file_meta/' + file_url.substring(file_url.lastIndexOf('/') + 1) + '/' + file_name
    dataType: 'json').done((file_meta) ->
    #console.log(file_meta.modified);
    btn = $('#PDF_btn')
    btn.attr 'title', '  * Last Edited  ' + new Date(file_meta.modified).toLocaleFormat('%m/%d/%y, %I:%M%p').toLowerCase() + '  '
    # console.log(daydiff(parseDate(get_today()).val()), parseDate($(file_meta.modified).val()));
    date1 = new Date(file_meta.modified)
    date2 = new Date(get_today())
    timeDiff = Math.abs(date2.getTime() - date1.getTime())
    diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24))
    # var s_bar = '<div id="pdf_modified">&nbsp;</div>';
    if diffDays <= 7
      btn[0].innerHTML = btn[0].innerHTML + '<div style="display: inline; float: right; color: #d00;"> ***</div>'
      # $('#pdf_modified').css( { 'width' : '8px', 'background-color' : '#0d0',  'display' : 'inline', 'float' : 'right' } );
    else if diffDays <= 30
      btn[0].innerHTML = btn[0].innerHTML + ' <div style="display: inline; float: right; color: #0d0;"> **</div>'
      # $('#pdf_modified').css( { 'width' : '8px', 'background-color' : '#00f',  'display' : 'inline', 'float' : 'right' } );
    else if diffDays <= 60
      btn[0].innerHTML = btn[0].innerHTML + ' <div style="display: inline; float: right; color: #00f;"> *</div>'
      # $('#pdf_modified').css( { 'width' : '8px', 'background-color' : '#00f',  'display' : 'inline', 'float' : 'right' } );
    return
  )
  return

get_today = ->
  today = new Date()
  dd = today.getDate()
  mm = today.getMonth() + 1
  #January is 0!
  yyyy = today.getFullYear()
  if dd < 10
    dd = '0' + dd
  if mm < 10
    mm = '0' + mm
  mm + '/' + dd + '/' + yyyy

###*************************************************************************************************
#                            Plot PRF files
*************************************************************************************************
###

plot_PRF = (prf_file) ->
  drawings[prf_file.substring(prf_file.lastIndexOf('/'), prf_file.lastIndexOf('.'))] = $.ajax(
    dataType: 'json'
    url: '/plot_prf' + prf_file).done((drawing_json) ->
    # console.log('plot complete');
    $('#drawing_message').html 'Plot sent... ' + prf_file
    $('#drawing_message').css 'display', 'normal'
    $('#drawing_message').delay(500).fadeIn 'normal', ->
      $(this).delay(5500).fadeOut()
      return
    return
  )
  return

###*************************************************************************************************
#                            Generate Plot menu
*************************************************************************************************
###

plot_menu = (sType, drawing_link) ->
  sImplemented = ''
  if sType == 'PDF'
    sImplemented = ' [not implemented yet]'
  else
    sImplemented = ''
  sHtml = '<div class="dropdown">' + '<button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1"' + 'data-toggle="dropdown" aria-expanded="true">' + 'Plot ' + sType + sImplemented + ' ' + '<span class="caret"></span>' + '</button>' + '<ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu1">'
  $.each sorted_printers, (index) ->
    key = sorted_printers[index]
    # console.log('printers: ', printers_json.responseJSON[key], drawing_link);
    sHtml += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#" onClick=\'plot_' + sType + '("/' + key + drawing_link + '"); return false;\' >' + printers_json.responseJSON[key] + '</a></li>'
    return
  sHtml += '</ul></div>'
  sHtml

get_printers_menu = ->
  # $('#menu_more').empty();
  #$('#menu_more').append('&nbsp;&nbsp;&nbsp; -- select a printer --');
  $('#printers_menu').empty()
  $('#printers_menu').append '<li class="dropdown-header">&nbsp;&nbsp;&nbsp;&nbsp;select a default printer</li>'
  $.each sorted_printers, (index) ->
    key = sorted_printers[index]
    s_default = ''
    # console.log(key === default_printer);
    if key == default_printer
      s_default = ' => '
    $('#printers_menu').append '<li id="' + key + '"><a href="#">' + s_default + printers_json.responseJSON[key] + '</a></li>'
    return
  return

get_default_printer = ->
  get_printer = $.ajax(
    dataType: 'text'
    url: '/api/get_printer/').done(->
    s_default_printer = get_printer.responseText
    if s_default_printer == 'no cookie'
      #default_printer = 'LaserBsize'
      default_printer = 'no cookie'
    else
      # console.log('default_printer: ' + get_printer.responseText);
      default_printer = s_default_printer
    get_printers_menu()
    return
  )
  return

set_default_printer = (default_printer) ->
  set_printer = $.ajax(
    dataType: 'text'
    url: '/api/set_printer/' + default_printer).done(->
    s_default_printer = set_printer.responseText
    # console.log('default_printer: ' + s_default_printer);
    default_printer = s_default_printer
    get_printers_menu()
    return
  )
  return

get_summary = ->
  console.log(' begin get_summary')
  summary = $.ajax(
    dataType: 'text'
    url: '/api/is_summary/').done(->
      console.log('> is_summary: ', summary.responseText)
      is_summary = summary.responseText
      return summary.responseText
    )

get_more_menu = ->
  selected_el = $('.active')[0]
  # $('#' + $('.btn_actions')[0].id).trigger('click'); 
  $('#menu_more').css 'display', 'block'
  p_top = $('#More_btn').parent()[0].offsetTop + 171 - $('#list').scrollTop()
  p_left = $('#More_btn').position().left + 154
  if /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    p_left = p_left - 221
  if /iPhone/i.test(navigator.userAgent)
    p_top = p_top + 51
    p_left = p_left - 9
  $('#menu_more').offset
    top: p_top
    left: p_left
  $('#menu_more').css 'display': 'block'
  return

get_misplaced_files = ->
  misplaced_files_json = $.ajax(
    datatype: 'json'
    url: '/api/get_misplaced_files').done(->
        misplaced_files = JSON.parse(misplaced_files_json.responseText)
        sOutput = ''
        console.log('misplaced folders: ', Object.keys(misplaced_files).sort())
        sorted_folders = Object.keys(misplaced_files).sort()
        console.log('sorted_folders: ', sorted_folders)
        $.each sorted_folders, (folder_index) ->
          folder = sorted_folders[folder_index]
          console.log('index: ', folder_index, folder)
          $('#list_misplaced_files').append '<h3>' + folder + '</h3>'
          $('#list_misplaced_files').append '<p> [allowed: ' + misplaced_files[folder].allowed + ']</p><ul>'
          $.each misplaced_files[folder].misplaced_files, (file) ->
            $('#list_misplaced_files').append '<li>' + misplaced_files[folder].misplaced_files[file] + '</li>'
          $('#list_misplaced_files').append '</ul><hr>'


        return
  )
  return

$(document).on 'click', '#more_info', ->
  more_info_json = $.ajax(
    dataType: 'json'
    url: '/api/get_mb_notes/' + $(this).attr('data-id')).done(->
    oMoreInfo = JSON.parse(more_info_json.responseText)
    key = Object.keys(oMoreInfo)[0]
    sInfo = '<h4><span class="label label-default">Job: </span></h4>' + key + '<br>'
    sInfo += '<h4><span class="label label-default">Description: </span></h4>'
    if oMoreInfo[key].description
      sInfo += oMoreInfo[key].description
    sInfo += '<br>'
    sInfo += '<div><h4><span class="label label-default">Notes: </span></h4><ul>'
    for note of oMoreInfo[key].notes
      if oMoreInfo[key].notes[note]
        sInfo += '<li class="list-group-item">' + oMoreInfo[key].notes[note] + '</li>'
    sInfo += '</ul>'
    $('#info').html sInfo
    $('#notes').show()
    return
  )
  return

###*************************************************************************************************
#                            Click on mb drawing list button
*************************************************************************************************
###

$(document).on 'click', '#mb_drawing_list', ->
  mb_drawings_json = $.ajax(
    dataType: 'json'
    url: '/api/get_mb_drawings/' + $(this).attr('data-id')).done(->
    oMbDrawings = JSON.parse(mb_drawings_json.responseText)
    key = Object.keys(oMbDrawings)[0]
    if typeof key == 'undefined'
      $('#flash').html ' Masterbill data not available -- from Accuterm generate Masterbill'
      $('#returned_count').addClass 'alert alert-info'
      flash_message()
      return false
    sorted_drawings = Object.keys(oMbDrawings[key]).sort()
    # console.log(sorted_drawings);
    # console.log(oMbDrawings);
    sHTML = '<h3><span class="label label-info">Master bill of materials drawing list: </span></h3>[ beta test - report inaccuracies ]<br><br><ul>'
    $.each sorted_drawings, (index) ->
      sHTML += '<li class="list-group-item" onClick="window.open(\'/q/' + sorted_drawings[index] + '\', \'_blank\')"' + ' title="' + sorted_drawings[index] + '">' + oMbDrawings[key][sorted_drawings[index]] + '<img src="static/img/link_icon.gif" class="link_icon"></li>'
      return
    sHTML += '</ul>'
    $('#info').html sHTML
    $('#notes').show()
    return
  )
  return

###*************************************************************************************************
#                            Click on media list button
*************************************************************************************************
###

$(document).on 'click', '#media_list', ->
  media_json = $.ajax(
    dataType: 'json'
    url: '/api/get_media/' + $(this).attr('data-id')).done(->
    oMedia = JSON.parse(media_json.responseText)
    key = Object.keys(oMedia)[0]
    if typeof key == 'undefined'
      $('#flash').html ' Media data not available'
      $('#returned_count').addClass 'alert alert-info'
      flash_message()
      return false
    sorted_media = Object.keys(oMedia[key]).sort()
    # console.log(sorted_drawings);
    # console.log(oMedia, key)
    sHTML = '<h3><span class="label label-info">Media list: </span></h3>[ beta test - report inaccuracies ]<br><br><ul>'
    $.each sorted_media, (index) ->
      sHTML += '<li class="list-group-item media_list_folder" title="' + oMedia[key][sorted_media[index]] + '" data-id="' + encodeURIComponent(oMedia[key][sorted_media[index]]) + '">' + oMedia[key][sorted_media[index]].substring(oMedia[key][sorted_media[index]].indexOf(key)) + '<img src="static/img/link_icon.gif" class="link_icon"></li>'
      #  onClick="window.open(\'/api/get_media_folder/' + encodeURIComponent(oMedia[key][sorted_media[index]]) + '\', \'_blank\')"' + '
      return
    sHTML += '</ul>'
    $('#info').html sHTML
    $('#notes').show()
    return
  )
  return

###*************************************************************************************************
#                            Click on media list folder 
*************************************************************************************************
###

$(document).on 'click', '.media_list_folder', ->
  data_id = $(this).attr('data-id')
  media_json = $.ajax(
    dataType: 'json'
    url: '/api/get_media_folder/' + $(this).attr('data-id')).done(->
      oMedia = JSON.parse(media_json.responseText)
      key = Object.keys(oMedia)[0]
      if typeof key == 'undefined'
        $('#flash').html ' Media data not available'
        $('#returned_count').addClass 'alert alert-info'
        flash_message()
        return false
      sorted_media = Object.keys(oMedia[key]).sort()
      sHTML = ''      # '<section data-featherlight-gallery>'
      $.each sorted_media, (index) ->
        # console.log( '/api/get_image/' + data_id + '/' + oMedia[key][sorted_media[index]])
        sHTML += '<a class="gallery" href="/api/get_image/' + data_id + '/' + oMedia[key][sorted_media[index]] + '"  data-featherlight-gallery="/api/get_image/' + data_id + '/' + oMedia[key][sorted_media[index]] + '"><img src="/api/get_image/' + data_id + '/' + oMedia[key][sorted_media[index]] + '"></a>&nbsp;'
        # console.log('**', oMedia[key][sorted_media[index]])
        # sHTML += '</section>'
      $('#media').html(sHTML)
      $('a.gallery').featherlightGallery({ gallery: { next: 'next »', previous: '« previous'}})
      $('a.gallery')[0].click()
      console.log($('a.gallery'))
  )
  return


###*************************************************************************************************
#                            Click on More menu button
*************************************************************************************************
###

# $(document).on('click', '#More_btn', function() {
#   get_more_menu();
# });

###*************************************************************************************************
#                            Press key
*************************************************************************************************
###

$(document).keydown (e) ->
  next_el = undefined
  $('#menu_more').hide()
  switch e.keyCode
    # forward slash
    when 191, 69
      # key is e 
      if $('#search').is(':focus')
        $('#search').val $('#search').val() + 'e'
        # keeping typing
        return false
      else
        $('#search').focus()
        $('#search').select()
        return false
        #"return false" will avoid further events
    when 13
      #key enter
      update_list()
    # down arrow
    # fall through 
    when 40, 74
      # j key
      if $('#search').is(':focus')
        $('#search').val $('#search').val() + 'j'
        # keeping typing
        return false
      else
        selected_el = $('.active')[0]
        if selected_el.nextSibling
          next_el = $(selected_el.nextSibling)
          next_el.trigger 'click'
          # sets next_el to active
          if next_el[0].offsetTop < $('#list').scrollTop()
            # overflow
          else
            # no overflow
            $('#list').scrollTop 0
            $('#list').scrollTop next_el.position().top - $('#list').height() + 45
      return false
    # up arrow
    # fall through
    when 38, 75
      # k key
      selected_el = $('.active')[0]
      if selected_el.previousSibling
        next_el = $(selected_el.previousSibling)
        next_el.trigger 'click'
        # sets next_el to active
        if next_el[0].offsetTop < $('#list').scrollTop()
          $('#list').scrollTop 0
          $('#list').scrollTop next_el.position().top
        else
          # no overflow
    when 80
      # p key
      selected_el = $('.active')[0]
      $('#' + $('.btn_actions')[2].id).trigger 'click'
    when 68
      # d key
      selected_el = $('.active')[0]
      $('#' + $('.btn_actions')[1].id).trigger 'click'
    when 77
      # m key
      if show_more_menu
        $('#menu_more').hide()
        $('#More_btn').css
          'background-color': more_btn_background
          'color': more_btn_color
        show_more_menu = false
      else
        show_more_menu = true
        $('#More_btn').css
          'background-color': '#f00'
          'color': '#fff'
          'background': 'red'
        get_more_menu()
  return
  #using "return" other attached events will execute

###*************************************************************************************************
#                            Document ready
*************************************************************************************************
###

$(document).ready ->
  locationPath = window.location.pathname.split('/')
  q = locationPath[2]
  if q != undefined
    $('#search').attr 'value', q
    update_list()
    $('#search').focus ->
      $('#search').select()
      return
    $('#search').focus
  else
    #
  $('.gallery').featherlightGallery()
  $('#fsearch').on 'submit', (event) ->
    event.preventDefault()
    update_list()
    return
  $('#search').on 'click', (event) ->
    $('#search').val ''
    false
  $('body').on 'click', '.btn_actions', (event) ->
    # console.log('click ', $(this)[0] );
    handle_action_clicks $(this)[0]
    event.stopPropagation()
    return
  $('body').on 'click', '#Search', (event) ->
    # console.log('click ', $(this)[0] );
    $('#Search').val ''
    $('#search').focus()
    $('#search').focus ->
      $('#search').select()
      return
    event.stopPropagation()
    return
  $('body').on 'click', '.pdf', ->
    # console.log('click ', $(this)[0] );
    handle_results_clicks $(this)[0]
    return
  $('body').on 'click', '#printers_menu li', (e) ->
    default_printer = e.currentTarget.id
    set_default_printer default_printer
    get_printers_menu()
    $('#flash').html ' Default printer changed to ' + printers_json.responseJSON[default_printer]
    $('#returned_count').addClass 'alert alert-info'
    flash_message()
    return

  $('body').on 'click', '#reports_menu li', (e) ->
    console.log('misplaced_files_menu:', e)

    get_misplaced_files()

    $('#list_queue').empty()
    $('#misplaced_files').css
      'display': 'block'
    return e

  $('body').on 'click','.download_file', (event) ->
    data_id = this.attributes['data-id'].value
    #console.log('  > ', data_id)
    download_file(this.attributes['data-id'].value)
    return

  $('#list').on 'scroll', ->
    $('#menu_more').hide()
    $('#More_btn').css
      'background-color': more_btn_background
      'color': more_btn_color
    show_more_menu = false
    return
  $(document).on 'click', (event) ->
    $('#menu_more').hide()
    $('#More_btn').css
      'background-color': more_btn_background
      'color': more_btn_color
    show_more_menu = false
    return

  $('#btn_summary').on 'click', ->
    if is_summary
      $('#btn_summary').val('Showing all files')
      $('#btn_summary').prop('title', "  Click to show Drawings only  ")
      more_btn_background = '#eee'
      more_btn_color = '#ccc'
      #$('#btn_summary').removeClass('btn-primary')
      #$('#btn_summary').addClass('btn-info')
      #$('#summary-icon').prop('src', '/static/img/all-files.png')
      is_summary = false
      update_list()
    else
      $('#btn_summary').val('Showing drawings only')
      $('#btn_summary').prop('title', "  Click to show All files  ")
      more_btn_background = '#fff'
      more_btn_color = 'rgb(85, 85, 255)'
      ##$('#btn_summary').removeClass('btn-info')
      #$('#btn_summary').addClass('btn-primary')
      #$('#summary-icon').prop('src', '/static/img/drawing.png')
      is_summary = true
      update_list()

  ###*************************************************************************************************
  #                            Search text box has focus
  *************************************************************************************************
  ###

  $(document).on 'focus', '#search', ->
    $(this).attr 'value', ''
    return

  ###*************************************************************************************************
  #                            Search text box changed
  *************************************************************************************************
  ###

  $(document).on 'blur', '#search', ->
    $(this).attr 'value', 'search for drawings...'
    return

  ###*************************************************************************************************
  #                            Click on Search button
  *************************************************************************************************
  ###

  $(document).on 'click', '#submit', ->
    update_list()
    return

  ###************************************************************************************************###

  get_default_printer()
  printers_json = $.ajax(
    dataType: 'json'
    url: '/api/get_printers/').done((printers_json) ->
    for key of printers_json
      sorted_printers[sorted_printers.length] = key
    sorted_printers.sort()
    $.each sorted_printers, (index) ->
      # var key = sorted_printers[index];
      return
    get_printers_menu()
    return
  )
  return
