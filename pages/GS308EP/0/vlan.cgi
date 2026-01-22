<div class='box_css'>
<div class="box-wrapper">
  <div class="box-header">VLAN</div>
  <div class="desc">ml141 <span class="sub-txt">ml771</div>
</div>
<div class="vlan-wrapper clearfix">
<div bind="vlan-mod" class="vlan-left-view fadeInRight animated cmn-animation">
  <div class="preset-box">
    <ul class="list-5">
      <li>
        <span id='fixPos' vlan-mod-str='957' class="header">ml627</span>
        <p class="desc">ml636</p>
        <div class='hide'><span class="icon-tick"></span><span class="sub-txt">ml571</span></div>
        <button name='noVlan' vlan-mod="noVlan" mod-num='0' class="btn-add">ml118</button>
      </li>
      <li>
        <span vlan-mod-str='958' class="header">ml735</span>
        <p class="desc">ml427</p>
        <div class='hide'><span class="icon-tick"></span><span class="sub-txt">ml571</span></div>
        <button name='bscPotBsd' vlan-mod="bscPotBsd" mod-num='1' class="btn-add">ml118</button>
      </li>
      <li>
        <span vlan-mod-str='959' class="header">ml829</span>
        <p class="desc">ml195</p>
        <div class='hide'><span class="icon-tick"></span><span class="sub-txt">ml571</span></div>
        <button name='advPotBsd' vlan-mod="advPotBsd" mod-num='2' class="btn-add">ml118</button>
      </li>
      <li>
        <span vlan-mod-str='960' class="header">ml543</span>
        <p class="desc">ml912</p>
        <div class='hide'><span class="icon-tick"></span><span class="sub-txt">ml571</span></div>
        <button name='bsc8021Q' vlan-mod="bsc8021Q" mod-num='3' class="btn-add">ml118</button>
      </li>
      <li>
        <span vlan-mod-str='961' class="header">ml428</span>
        <p class="desc">ml522</p>
        <div class='hide'><span class="icon-tick"></span><span class="sub-txt">ml571</span></div>
        <button name='adv8021Q' vlan-mod="adv8021Q" mod-num='4' class="btn-add">ml118</button>
      </li>
    </ul>
  </div>
</div>
<div bind="vlan-content" class="vlan-right-view animated cmn-animation fadeInRight">
<section vlan-page="adv8021Q">
  <div main='4' class="fadeInRight animated cmn-animation wid-expand">
    <div class="box-sub">
      <div class="header">ml428</div>
      <div class="desc">ml582</div>
    </div>
    <div class="tab-container">
      <div class="tab-top tab-pad cols-3 wrap">
        <span>ml408</span><span>ml708</span><span>ml717</span>
      </div>
      <ul bind='btns-4' class="tab-init">
        <li class="tab-pad">
          <div li-header class="li-header cols-3 child-v-top">
            <span vid-4><i class="phone-wrap"></i>1</span><span vnm-4 class="hid-txt" untrans>Default</span><span>1 2 3 4 5 6 7 8 <i tab-arrow class="tab-arrow icon-expand"></i></span>
          </div>
          <input hidden-mem type='hidden' value='22222222'>
          <div li-btn class="li-btn">
            <button name='editAdvQVlan1' edit-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltAdvQVlan1' delete-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad">
          <div li-header class="li-header cols-3 child-v-top">
            <span vid-4><i class="phone-wrap"></i>100</span><span vnm-4 class="hid-txt" untrans>Internal</span><span>2 3 4 5 6 7 8 <i tab-arrow class="tab-arrow icon-expand"></i></span>
          </div>
          <input hidden-mem type='hidden' value='31222222'>
          <div li-btn class="li-btn">
            <button name='editAdvQVlan100' edit-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltAdvQVlan100' delete-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
      </ul>
      <input id='voVid' type='hidden' value='0'>
      <div class="tab-bottom"><button name='addAdvQVlan' onclick="VlanAdvQ.addVlan()" hide="[main='4']" show="[detail='4']" class="btn-add">ADD VLAN</button></div>
    </div>
    <div class="box-sub">
      <div class="header">ml142</div>
      <div class="desc" withsubtag>ml406</div>
    </div>
  </div>
  <div detail='4' class="fadeInRight animated cmn-animation hide">
    <div class="header adjust-3">ml428</div>
    <div class="txt-area">
      <div>ml215</div>
      <input id='vnm-4' maxlength="14" type="text" value="">
    </div>
    <div class="txt-area">
      <div>ml209</div>
      <input id='vid-4' maxlength="4" type="text" value="">
    </div>
    <div class="desc" style="margin: 25px 0 10px;">ml582</div>
    <div class="tab-container">
      <div bind="sel-all" class="tab-top tab-pad tab-pad-resp btn-right clearfix">
        <span style='float:left;'>Port</span>
        <button name='eAll' sel-all="3" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">Exclude All</button>
        <button name='uAll' sel-all="2" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">Untag All</button>
        <button name='tAll' sel-all="1" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">Tag All</button>
      </div>
      <ul id='potTypList' bind="pot-typ" class="tab-init common-tab">
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 1 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 2 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 3 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 4 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 5 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 6 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 7 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
        <li class="tab-pad tab-pad-resp inline-div">
          <div class="pot-num-wrap">
            <span><b common>Port</b> 8 -&nbsp;</span><span unname class="hid-txt">unnamed</span>
          </div>
          <div class="pot-icon-wrap right">
            <span pot-typ="1">T</span><span pot-typ="2">U</span><span pot-typ="3" class="seld-pot">E</span>
          </div>
        </li>
      </ul>
    </div>
    <div class="item">
      <div class="header">ml641</div>
      <div class="desc adjust">ml601</div>
      <div class="clearfix">
        <div class="checkbox"><input id="voVlanState" type="checkbox" onclick='initVoState()'><label></label></div>
      </div>
    </div>
    <div id="voVlanContent" class='hide'>
      <div class="item">
        <div class="header">ml190</div>
        <div class="desc adjust">ml962</div>
        <div class="dropdown" style="max-width: 200px;">
          <p class="dropdown-toggle" name="dropdownToggle" data-toggle="dropdown">
            <span id='cos' class="selectItem">6</span><span class="dropdown_icon icon-expand"></span>
          </p>
          <ul class="dropdown-menu">
            <li class="waves-effect waves-gray"><a>0</a></li>
            <li class="waves-effect waves-gray"><a>1</a></li>
            <li class="waves-effect waves-gray"><a>2</a></li>
            <li class="waves-effect waves-gray"><a>3</a></li>
            <li class="waves-effect waves-gray"><a>4</a></li>
            <li class="waves-effect waves-gray"><a>5</a></li>
            <li class="waves-effect waves-gray"><a>6</a></li>
            <li class="waves-effect waves-gray"><a>7</a></li>
          </ul>
          <input class="hidValue" value="" type="hidden">
        </div>
      </div>
      <div class="item">
        <div class="header">ml463</div>
        <div class="desc adjust" withsubtag>ml513</div>
      </div>
    </div>
    <input type='hidden' id='vlanNum' value='2'>
    <div class="submit_btn">
      <span class="text-primary">
<button name='submitAdvQVlanCfg' onclick="VlanAdvQ.submitVlanCfg()" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">APPLY</button>
      </span>
      <span class="text-muted">
<button name='cancelAdvQVlanCfg' hide="[detail='4']" show="[main='4']" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini">CANCEL</button>
      </span>
    </div>
  </div>
  <div detail='pvidMain' class="fadeInRight animated cmn-animation wid-expand hide">
    <div class="box-sub">
      <div class="header">ml223</div>
      <div class="desc">ml582</div>
    </div>
    <div class="tab-container">
      <div class="tab-top tab-pad cols-2">
        <span>Port</span><span>ml467</span>
      </div>
      <ul bind="pvid-tab" class="tab-init common-tab pvid-tab">
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">1</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">2</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">3</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">4</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">5</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">6</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">7</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
        <li class="tab-pad cols-2">
          <div class="pot-box">
            <div class="pot-icon-wrapper"><span class="li-icon-pot icon-pot-empty"></span><span class="pot-num">8</span></div>
            <div class="pot-nam"><span unname class="hid-txt wid-full">unnamed</span></div>
          </div>
          <div>
            <span pvid-str class="hid-txt adjust-1">1*, 100, </span>
            <i class="tab-arrow icon-expand arrow-right"></i>
          </div>
        </li>
      </ul>
    </div>
    <div class="submit_btn">
      <span class="text-primary">
      <button name='pvidBack' hide="[detail='pvidMain']" show="[main='4']" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">BACK</button>
      </span>
    </div>
  </div>
  <div detail='pvidDetail' class="fadeInRight animated cmn-animation hide">
    <div id="potBox" class="pot-box sigle-pot"></div>
    <div class="dropdown adjust-2">
      <p class="dropdown-toggle" name="dropdownToggle" data-toggle="dropdown">
        <span name='curPvidTxt' id='curPvidTxt' pvid class="selectItem hid-txt adjust-4">1 - Default</span><span class="dropdown_icon icon-expand"></span>
      </p>
      <ul class="dropdown-menu">
        <li class="waves-effect waves-gray"><a class='hid-txt vlan1'>1 - Default</a></li>
        <li class="waves-effect waves-gray"><a class='hid-txt vlan100'>100 - Internal</a></li>
      </ul>
      <input class="hidValue" value="" type="hidden">
    </div>
    <div class="submit_btn">
      <span class="text-primary">
      <button name='submitPvid' onclick="VlanAdvQ.submitPvid()" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">APPLY</button>
      </span>
      <span class="text-muted">
      <button name='cancelPvid' hide="[detail='pvidDetail']" show="[detail='pvidMain']" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini">CANCEL</button>
      </span>
    </div>
  </div>
  <div detail='ouiMain' class="fadeInRight animated cmn-animation wid-expand hide">
    <div class="box-sub" style="margin: 0 0 15px;">
      <div class="header">ml641</div>
    </div>
    <div class="tab-container">
      <div class="tab-top tab-pad cols-2">
        <span>ml491</span><span>ml728</span>
      </div>
      <ul bind='btns-oui-4' id="ouiTab" class="tab-init">
        <li class="tab-pad" oui-num='INDEX_1'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:01:E3</span><span desc untrans>SIEMENS<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui1' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui1' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_2'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:03:6B</span><span desc untrans>CISCO1<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui2' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui2' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_3'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:04:0D</span><span desc untrans>AVAYA1<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui3' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui3' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_4'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:04:13</span><span desc untrans>SNOM<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui4' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui4' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_5'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:12:43</span><span desc untrans>CISCO2<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui5' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui5' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_6'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:1B:4F</span><span desc untrans>AVAYA2<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui6' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui6' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_7'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:60:B9</span><span desc untrans>NITSUKO<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui7' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui7' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_8'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:D0:1E</span><span desc untrans>PINTEL<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui8' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui8' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_9'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:E0:75</span><span desc untrans>VERILINK<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui9' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui9' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
        <li class="tab-pad" oui-num='INDEX_10'>
          <div li-header-2 class="li-header cols-2">
            <span tele untrans>00:E0:BB</span><span desc untrans>3COM<i tab-arrow-2 class="tab-arrow icon-expand"></i></span>
          </div>
          <div li-btn-2 class="li-btn">
            <button name='editOui10' edit-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">EDIT</button>
            <button name='deltOui10' delete-oui-4 data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">DELETE</button>
          </div>
        </li>
      </ul>
      <div class="tab-bottom"><button name='addOui' onclick="VlanAdvQ.addOui()" hide="[detail='ouiMain']" show="[detail='ouiDetail']" class="btn-add">ADD OUI</button></div>
    </div>
    <div class="submit_btn">
      <span class="text-primary">
      <button name='ouiBack' hide="[detail='ouiMain']" show="[detail='4']" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">BACK</button>
      </span>
    </div>
  </div>
  <div detail='ouiDetail' class="fadeInRight animated cmn-animation hide">
    <div class="header adjust-3">ml508</div>
    <div class="txt-area">
      <div>ml274</div>
      <input id='tele' maxlength="8" type="text" value="">
    </div>
    <div class="txt-area">
      <div>ml728</div>
      <input id='desc' maxlength="32" type="text" value="">
    </div>
    <div class="submit_btn" style="margin-top: 30px;">
      <span class="text-primary">
      <button name='submitOui' onclick="VlanAdvQ.submitOui()" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">APPLY</button>
      </span>
      <span class="text-muted">
      <button name='cancelOui' hide="[detail='ouiDetail']" show="[detail='ouiMain']" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini">CANCEL</button>
      </span>
    </div>
  </div>
</section>
</div></div>
</div>
<input type=hidden id='hash' value="1dfccf382d99b5cb19d4371078c3c8a5">
<input type=hidden id='vlanMod' value="4">
<script type="text/javascript">
function initVlanModSet(){
  $("[bind='vlan-mod']").on("click", "[vlan-mod]", function(){
    var modMsg = $(this).parents('li').find('[vlan-mod-str]').attr('vlan-mod-str');
    toggleModalWindow('submit', "VLAN", 'ml' + modMsg, "CONTINUE");
    VlanMod.vlanModFlag = $(this).attr('mod-num');
  });
}
function initVlanModIcon(){
  var vlanMod = $('#vlanMod').val(),
      curModBtn = $("[mod-num=" + "'" + vlanMod + "'" + "]");
  curModBtn.addClass('hide');
  curModBtn.prev().removeClass('hide');
  curModBtn.parents('li').addClass('active');
}
function initShowBox(){
  $("[bind='vlan-content']").on("click", "[hide]", function(){
    $($(this).attr("hide")).addClass("hide");
  });
  $("[bind='vlan-content']").on("click", "[show]", function(){
    $($(this).attr("show")).removeClass("hide");
  });
  $("[bind='mult-titl']").on("click", ".mult-titl > li", function(){
    $(this).siblings().removeAttr("active");
    $(this).attr("active", "active");
  });
  $("[bind='pvid-tab']").on("click", ".pvid-tab > li", function(){
    $("#potBox").html($(this).find(".pot-box").html());
    $("[detail='pvidMain']").addClass("hide");
    $("[detail='pvidDetail']").removeClass("hide");
    $("#curPvidTxt").html($(".vlan1").html());
  });
}
function initSelBtn(){
  $("#selAll").click(function(){
    $(".pot-check").prop("checked", true);
  });
  $("#rvmAll").click(function(){
    $(".pot-check").prop("checked", false);
  });
  $("[bind='sel-all']").on("click", "[sel-all]", function(){
    $("[pot-typ]").removeClass('seld-pot');
    $("[pot-typ=" + "'" + $(this).attr('sel-all') + "'" + "]").addClass('seld-pot');
  });
  $("[bind='pot-typ']").on("click", "[pot-typ]", function(){
    $(this).siblings().removeClass('seld-pot');
    $(this).addClass('seld-pot');
  });
}
function initPotMod(){
  $('[pot-mod]').each(function(){
    var ele = $(this).find('[' + $(this).attr('pot-mod') + ']');
    ele.siblings().addClass('hide');
    ele.removeClass('hide');
  });
}
function initDropPvidComma(){
    $('[pvid-str]').each(function(){
        $(this).text($(this).text().substring(0, $(this).text().length-2));
    });
}
function initVoState(){
    if($('#voVlanState').prop('checked')){
        $('#voVlanContent').removeClass('hide');
    }else{
        $('#voVlanContent').addClass('hide');
    }
}
function getTransStr(){
    var $ele = $('#vlanAdvP-vlan-id-des');
    var tmpTxt = $ele.text();
    if (tmpTxt) {
        $ele.text(MultLang.transParmLang(tmpTxt));
    }
}
$(document).ready(function(){
  getTransStr();
  $(".dropdown-toggle").each(function(){dropdownMenu(this);});
  selectOptions();
  collapseOrExpandBlock($('[li-header]'), $('[li-btn]'), $('[tab-arrow]'));
  collapseOrExpandBlock($('[li-header-2]'), $('[li-btn-2]'), $('[tab-arrow-2]'));
  initVlanModIcon();
  initShowBox();
  initSelBtn();
  initVlanModSet();
  initPotMod();
  initDropPvidComma();
  initVoState();
  VlanAdvP.initDelVlan();
  VlanAdvP.initEdtVlan();
  VlanBscQ.initPotModSel();
  VlanBscQ.initDelVlan();
  VlanBscQ.initEdtVlan();
  VlanAdvQ.initDelVlan();
  VlanAdvQ.initEdtVlan();
  VlanAdvQ.initDelOui();
  VlanAdvQ.initEdtOui();
  VlanAdvQ.initSaveData();
  VlanAdvQ.initRecoverData();
  transPage($('#transContent')[0]);
  initShowHidTxt();
  setTimeout(function(){$('#fixPos').css('display', 'inline-block');}, 500);
  $('.waves-effect').click(function(){initShowHidTxt();}, 200);
});
</script>
