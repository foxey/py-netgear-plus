<!DOCTYPE html>
<html>
<head>
</head>
<body onload="">
<div class="container">
<div class="row">
<div class="col-xs-12 col-xl-8 over_flow_hid" id="sys_info">
<div class="row">
<div class="col-xs-12 col-sm-4">
<div class="box_container">
<div class="box_css border_right_radius">
<div class="box_flex left_box_content">
<div class="margin_top">
<img class="icon_display icon_1" src="/switch-desktop.svg">
<div class="switch-nighthawk">
<div class="font_bold">ml396</div>
<div id="switch_name" untrans></div>
</div>
</div>
<div class="col_line"></div>
<div>
<a class="icon_display icon_2" onclick="document.getElementById('dashboard_port').scrollIntoView();">
<span>#</span>
</a>
<div class="switch-nighthawk">
<div class="font_bold">ml180</div>
<div class="font_bold">ml035</div>
</div>
</div>
</div>
</div>
</div>
</div>
<div id="dashboard_info" class="col-xs-12 col-sm-8" style="z-index:1;">
<div class="mid_border_margin">
<div class="box_css border_left_radius">
<div class="mid_row">
<div name='isShowSysinfo' class="mid_row_title">
<div class="info_header_content">
<div class="mid_title_icon icon_color_gray icon_sm accordion_icon" style="margin-right:0.75rem;">
<span class="icon-info-outline"></span></div>
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span></i>
<span style="color:#00d76f;">ml565</span></div></div>
<div id='sysinfoContainer' class="hid_info max_height">
<form name='sysInfo' method="post" action="switch_name.cgi">
<div class="hid_content row row-xs"><div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span>ml089</span></div>
<div><span>V1.0.1.3</span></div></div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>ml550</span></div>
<div id='supportDhDiv' withsubtag>ml791</div>
<input type="hidden" id="prctName" value="GS308Ev4" />
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>ml656</span></div>
<div><span>
<input id="switchName" name='switch_name' class="input-theme" style="width:130%;color:#fff;" oninput="enableButtons()" maxlength="20" role="input" value="sw-test" type="text">
</span></div></div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>ml678</span></div>
<div><span>54:07:7D:1A:B0:6A</span></div></div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>ml198</span></div>
<div><span>7H914553C0473</span></div></div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>ml040</span></div>
<div><span>GS308Ev4</span></div></div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title"><span>Language</span></div>
  <div style='padding:0 0 0 1.5rem;'><div class="dropdown" style="width:78%">
    <p onclick="dropdownMenu(this)" class="dropdown-toggle" name="dropdownToggle" data-toggle="dropdown">
      <span id='curLangTxt' class="selectItem" style='padding:0'>English</span><span class="dropdown_icon icon-collapse"></span>
    </p>
    <ul id='langList' class="dropdown-menu">
      <li value='at' class="waves-effect waves-gray"><a>Auto</a></li>
      <li value='en' class="waves-effect waves-gray"><a>English</a></li>
      <li value='de' class="waves-effect waves-gray"><a>Deutsch</a></li>
      <li value='ja' class="waves-effect waves-gray"><a>日本語</a></li>
    </ul>
    <input type="hidden" name='SET_LANG' id="selLang" class="hidValue" value="en">
  </div></div>
</div>
</div>
    <input type=hidden name='hash' id='hash' value="36972918d3ef224384991b279306afd4">
</form>
<div class= "submit_btn">
<span class="text-primary"><button name='submitSysinfo' onclick='submitSysInfo()' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini" disabled=''>
APPLY
</button></span>
<span class="text-muted"><button name='cancelSysinfo' onclick="cancelDashboard(this)" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini" disabled=''>
CANCEL
</button></span>
</div></div></div>
<div class="mid_row">
<div name='isShowPotled' class="mid_row_title">
<div class="info_header_content">
<div class="mid_title_icon icon_color_gray icon_sm accordion_icon" style="margin-right:0.75rem;">
<span class="icon-LED-outline"></span>
</div>
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i>
<span class="text_display padding_r_18 pull-right">
<span class="" id='led_switch'>ON</span>
</span>
<span style="color:#00d76f;">ml389</span>
</div>
</div>
<div class="hid_info" style='max-height:121px;'>
<div class="hid_box js_active">
<div class="clearfix" style="margin-left:3.5rem">
<div class="checkbox">
<input id='ledMod' type="checkbox" onclick="enableButtons()" checked/>
<label></label>
</div>
</div>
<div><div class="stealth_mode">
 <span>OFF</span><span>ml293</span></div>
<div class="stealth_mode"  style="color:#00d76f;margin-left:1rem">
 <span>ON</span><span>ml351</span></div></div>
<div class= "submit_btn">
<span class="text-primary"><button name='submitLed' onclick='submitLED()' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini" disabled=''>
APPLY
</button></span>
<span class="text-muted"><button name='cancelLed' onclick="cancelDashboard(this)" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini" disabled=''>
CANCEL
</button></span>
</div></div></div></div>
<div class="mid_row">
<div name='isShowDhcp' class="mid_row_title" onclick="getHidPage('ip_dhcp')">
<div class="info_header_content">
<div class="mid_title_icon icon_color_gray icon_sm accordion_icon" style="margin-right:0.75rem;">
<span class="icon-ip"></span>
</div>
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i>
<span style="font-weight:500;font-size:14px; color:#00d76f;">ml257</span>
<span id='dhcp_header' style="padding-left:1rem;">ml152</span>
<span class="text_display pull-right padding_r_18">
<span class="">192.168.0.239</span></span>
</div></div>
<div id='ip_dhcp' class="hid_info" style='max-height:370px;'>
</div></div>
<div class='mid_row'>
<input id="hiddenMem" value="00000000" type="hidden">
<div class='mid_row_title' onclick="redirectToLAGPage()">
<div class='info_header_content'>
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right"><span class="icon-expand icon-right"></span></i>
<div class='mid_title_icon icon_color_gray icon_sm accordion_icon' style='margin-right:0.75rem;'>
<span class='icon-lag-outline'><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></span>
</div>
<span class='text_display padding_r_18 pull-right' style='top: -.5rem;position: relative;'>
<span class='lag-content'>
<input type=hidden id='lag_1_state' value='Link Down'>
<div>LAG 1: <span id='lagState_1'></span> (<span id='lag'>ml394</span> <span id='lagPt1'></span>)</div>
<input type=hidden id='lag_2_state' value='Link Down'>
<div>LAG 2: <span id='lagState_2'></span> (<span id='lag'>ml394</span> <span id='lagPt2'></span>)</div>
</span></span>
<input type=hidden id='lag_num' value='2'>
<span style="font-weight:500;font-size:14px; color:#00d76f;">LAG</span>
</div></div></div>
</div></div></div></div></div>
<div class="col-xs-12 col-md-6 col-xl-4 over_flow_hid" id="dashboard_port">
<div class="box_css volumes-scss widget_height has-bottom-opacity-effect" id="port_list">
<div class="card-scss-header widget_header">
<div class="card_title widget_header_title">ml495</div></div>
<div class="box_flex" id="port_details">
<ul class="list_css">
<li class="list_item index_li">
<div name='isShowPot1' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span class="text-success-1">UP</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="1">
<span>1</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>1000M full</span>
<input type="hidden" class="LinkedSpeed" value="1000M full">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot1' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot2' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="2">
<span>2</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot2' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot3' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="3">
<span>3</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot3' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot4' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="4">
<span>4</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot4' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot5' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="5">
<span>5</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot5' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot6' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="6">
<span>6</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot6' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot7' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="7">
<span>7</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot7' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
<li class="list_item index_li">
<div name='isShowPot8' class="li_header_content">
<i class="mid_title_icon icon_color_gray icon_sm accordion_icon accordion_plus pull-right">
<span class="icon-expand"></span>
</i><span class=" padding_r_18 pull-right">
<span>AVAILABLE</span></span>
<span class="index_li_title">
<input type="hidden" class="port" value="8">
<span>8</span></span></div>
<input type="hidden" class="portName" value="">
<div class="port_info">
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml510</span></div>
<div>
<span>Auto</span>
<input type="hidden" class="Speed" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml382</span></div>
<div>
<span>No Speed</span>
<input type="hidden" class="LinkedSpeed" value="No Speed">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml126</span></div>
<div>
<span>No Limit</span>
<input type="hidden"  class="ingressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml086</span></div>
<div>
<span>No Limit</span>
<input type="hidden" class="egressRate" value="1">
</div>
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div class="hid_info_title">
<span class='hid-txt wid-full'>ml322</span></div>
<div>
<span>OFF</span></div>
<input type="hidden" readOnly="readOnly" class="flowCtr" value="2">
</div>
<div class="hid_info_cell col-xs-12 col-sm-6">
<div onclick="edit_port_info()" class="edit_btn">
<button name='editPot8' data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
EDIT
</button>
</div>
</div>
</div>
</li>
</ul></div></div>
<div class="box_css volumes-scss widget_height has-bottom-opacity-effect " id="port_edit">
<div class="card-scss-header widget_header">
<div class="card_title widget_header_title edit_port_id">
</div>
</div>
<div class="box_flex">
<div class="edit_port_info">
<div class="edit_item">
<span class="input_theme_bar input_theme_label input_label">ml042</span>
</div>
<input type="text" readOnly="readOnly" class="input-theme" id="portID" value="">
</div>
<div class="edit_port_info">
<div class="edit_item">
<span class="input_theme_bar input_theme_label input_label">ml234</span>
</div>
<input id="portName" class="input-theme" maxlength="16" role="input" value="" type="text">
<div class="hr">
<hr class="hr1">
<hr class="hr2" style="transform: scaleX(0);">
</div>
</div>
<div class="edit_port_info">
<div class="edit_item">
<span class="input_theme_bar input_theme_label input_label">ml510</span>
</div>
<div class="dropdown">
<p onclick="dropdownMenu(this)" class="dropdown-toggle"  name="dropdownToggle" data-toggle="dropdown">
<span name='speedTxt' class="selectItem speedText"></span>
<span class="dropdown_icon icon-expand"></span></p>
<ul class="dropdown-menu SpeedList" >
<li class="waves-effect waves-gray"><a >Auto</a></li>
<li class="waves-effect waves-gray"><a>Disable</a></li>
<li class="waves-effect waves-gray"><a>10M full</a></li>
<li class="waves-effect waves-gray"><a>100M full</a></li></ul>
<input type="hidden" id="speedSelect" class="hidVal" value=""></div>
<div class="hr">
<hr class="hr1">
<hr class="hr2" style="transform: scaleX(0);">
</div>
</div>
<div class="edit_port_info">
<div class="edit_item">
<span class="input_theme_bar  input_theme_label input_label">ml126</span>
</div>
<div class="dropdown">
<p onclick="dropdownMenu(this)" class="dropdown-toggle"  name="dropdownToggle" data-toggle="dropdown">
<span name='ingressTxt' class="selectItem IngressText"></span>
<span class="dropdown_icon icon-expand"></span></p>
<ul class="dropdown-menu IngressList" >
<li class="waves-effect waves-gray"><a >No Limit</a></li>
<li class="waves-effect waves-gray"><a>512 Kbit/s</a></li>
<li class="waves-effect waves-gray"><a >1 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>2 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >4 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >8 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>16 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >32 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>64 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >128 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >256 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>512 Mbit/s</a></li></ul>
<input type="hidden" id="IngressSelect" class="hidVal" value=""></div>
<div class="hr">
<hr class="hr1">
<hr class="hr2" style="transform:scaleX(0);">
</div>
</div>
<div class="edit_port_info">
<div class="edit_item">
<span class="input_theme_bar input_theme_label input_label">ml086</span>
</div>
<div class="dropdown">
<p onclick="dropdownMenu(this)" class="dropdown-toggle"  name="dropdownToggle" data-toggle="dropdown">
<span name='egressTxt' class="selectItem EgressText"></span>
<span class="dropdown_icon icon-expand"></span></p>
<ul class="dropdown-menu EgressList" >
<li class="waves-effect waves-gray"><a >No Limit</a></li>
<li class="waves-effect waves-gray"><a>512 Kbit/s</a></li>
<li class="waves-effect waves-gray"><a >1 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>2 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >4 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >8 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>16 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >32 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>64 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >128 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a >256 Mbit/s</a></li>
<li class="waves-effect waves-gray"><a>512 Mbit/s</a></li></ul>
<input type="hidden" class="hidVal" id="EgressSelect" value=""></div>
<div class="hr">
<hr class="hr1">
<hr class="hr2" style="transform: scaleX(0);">
</div>
</div>
<div class="flow_control">
<div class="flow_control_des">
<span class="input_theme_bar input_theme_label input_label">ml322
 <p style="color:#777;padding-top:3px;">ml081</p>
</span>
 </div>
<div class="checkbox" style='padding-top:16px;'>
 <input id="flowControlCheck" type="checkbox" checked="" value="">
 <label></label>
 </div>
</div>
<div class= "submit_btn port_status_btn">
<span class="text-primary"><button name='submitPotedit' onclick="submitPortEdit()" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
APPLY</button></span>
 <span class="text-muted"><button name='cancelPotedit' onclick="back_port_info()" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini">
CANCEL</button></span>
</div>
</div>
 </div>
</div>
</div>
</div>
<script type="text/javascript">
function initLangEvents(){
        curLangTxt = 'English';
        var langList = $('#langList > li');
    for(var i=0, len=langList.length; i<len; i++){
        if(langList.eq(i).attr('value') == $('#selLang').val()){
            curLangTxt = langList.eq(i).find('a').text();
        }
    }
    laterLangTxt = curLangTxt;
    if ($('#isAuto').val() === 'ENABLE') {
        $('#curLangTxt').text(MultLang.transLang('Auto')).attr('data-save', MultLang.transLang('Auto'));
    } else {
        $('#curLangTxt').text(curLangTxt).attr('data-save', curLangTxt);
    }
    langList.click(function(){
        enableButtons();
        laterLangTxt = $(this).find('a').text();
    });
}
function getProductName(){
    var $ele = $('#supportDhDiv a');
    var link = $ele.attr('href');
    var proName = $('#prctName').val();
    link = link.replace('GS308EP', proName);
    $ele.attr('href', link);
}
$(document).ready(function(){
    $(document).bind("click", function(e){
      if ($(e.target).closest(".ip_input").length == 0){
          $(".ip_input").each(
          function(e)
          {
            $(this).find(".hr2").css("transform","scaleX(0)");
          }
        );
      }
    });
    updataConnectedPortNum();
    initLangEvents();
    transPage($('#main-content')[0]);
    initShowHidTxt();
    getLagInfo();
    getProductName();
});
</script>
</body>
 </html>
