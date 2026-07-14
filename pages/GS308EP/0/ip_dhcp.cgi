<div class="hid_box">
<div class="text-muted ip_dhcp">
<span>DHCP</span>
<span style="color:#8d979c;">ml497</span></div>
<div class="clearfix">
<div class="checkbox">
<input id='dhcpMod' onclick='revertDHCPContent();enableButtons()' type="checkbox" checked>
<label></label>
<input id='dhcpModFlag' type="hidden" value="true">
<input id='ipStr' type="hidden" value="10.156.22.73">
<input id='netMaskStr' type="hidden" value="255.255.255.0">
<input id='gatewayStr' type="hidden" value="10.156.22.1">
</div>
</div>
<div class="ip_input">
<label for="ipAddr" class="ip-input-label">ml257</label>
<div class="ip-input-hint-text"></div><input maxlength='15' readonly id='ipAddr' role="input" value="10.156.22.73" type="text" onkeyup="inputEleKeyUp(this)" onclick="clickEleInput(this, '.ip_input')">
<div class='textLine' style='display:none;'>
<hr class="hr1">
<hr class="hr2">
</div>
</div>
<div id='dhcp_content'>
<div class="ip_input">
<label for="subMsk" class="ip-input-label">ml269</label>
<div class="ip-input-hint-text"></div><input maxlength='15' readonly id='subMsk' role="input" value="255.255.255.0" type="text" onkeyup="inputEleKeyUp(this)" onclick="clickEleInput(this, '.ip_input')">
<div class='textLine' style='display:none;'>
<hr class="hr1">
<hr class="hr2">
</div></div>
<div class="ip_input">
<label for="gatWay" class="ip-input-label">ml294</label>
<div class="ip-input-hint-text"></div><input maxlength='15' readonly id='gatWay' role="input" value="10.156.22.1" type="text" onkeyup="inputEleKeyUp(this)" onclick="clickEleInput(this, '.ip_input')">
<div class='textLine' style='display:none;'>
<hr class="hr1">
<hr class="hr2" style="transform: scaleX(0);">
</div></div></div>
<div id='dhcp_btn' class= "submit_btn">
<span class="text-primary"><button name='submitDhcp' disabled onclick="submitDHCP();disableBtns(this)" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_primary button_theme_mini button button_mini">
APPLY
</button></span>
<span class="text-muted"><button name='cancelDhcp' disabled onclick="getHidPage('ip_dhcp');disableBtns(this)" data-react-toolbox="button" class="toolbox_lib_button button_theme_flat button_theme_default button_theme_mini button button_mini">
CANCEL
</button></span>
</div></div>
<script type="text/javascript">$(document).ready(function(){transPage($('#ip_dhcp')[0]);});</script>
</body></html>
