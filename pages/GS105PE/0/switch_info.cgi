
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>Switch Information</title>
<link rel="stylesheet" type="text/css" href="/style.css?a1.6.0.14">
<script src="/frame.js?a1.6.0.14" type="text/javascript"></script>
<script src="/function.js?a1.6.0.14" type="text/javascript"></script>
<script language="JavaScript">
function getCookie(){
   var aCookie = document.cookie.split(";");
   for (var i = 0;i <aCookie.length;i++)
   {
    console.log(aCookie[i]);
   }
  }
function selectOptions()
{
    var dhcp_mode = document.getElementById('dhcpMode');
	if (dhcp_mode.options[0].selected == true)
	{
		document.forms[0].elements.refresh.disabled = true;
		document.forms[0].elements.ip_address.disabled = false;
		document.forms[0].elements.subnet_mask.disabled = false;
		document.forms[0].elements.gateway_address.disabled = false;
	}
	else if (dhcp_mode.options[1].selected == true)
	{
		document.forms[0].elements.refresh.disabled = false;
		document.forms[0].elements.ip_address.disabled = true;
		document.forms[0].elements.subnet_mask.disabled = true;
		document.forms[0].elements.gateway_address.disabled = true;
	}
}
function dhcpModeChange()
{
	var dhcp_mode = document.getElementById('dhcpMode');
	if (dhcp_mode.options[0].selected == true)
	{
		document.forms[0].elements.refresh.disabled = true;
		document.forms[0].elements.ip_address.disabled = false;
		document.forms[0].elements.subnet_mask.disabled = false;
		document.forms[0].elements.gateway_address.disabled = false;
	}
	else if (dhcp_mode.options[1].selected == true)
	{
		document.forms[0].elements.refresh.disabled = false;
		document.forms[0].elements.ip_address.disabled = true;
		document.forms[0].elements.subnet_mask.disabled = true;
		document.forms[0].elements.gateway_address.disabled = true;
	}
	popUpWindown('alert','DHCP Mode','Note: Changing the protocol mode will reset the IP configuration.');
}
function changeRefreshVal()
{
	var re_fresh = document.getElementById('refresh');
	if (re_fresh.checked)
	{
		re_fresh.value = "1";
	}
	else
	{
		re_fresh.value = "0";
	}
}
</script>
</head>
<body onload="initErrMsg('Switch Information');selectOptions();getCookie()">
<form method="post" action="/switch_info.cgi">
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdrTable('Switch Information', 'switchInformation');</script>
</tr><tr><td class="topTitleBottomBar" colspan='2'></td></tr>
<tr><td class="paddingTableBody" colspan='2'><table class="tableStyle" id="tbl2" style="width:728px;">
 <tr>
  <td width='300' class="padding14Top">Product Name</td>
  <td align="center" nowrap>GS105PE</td>
 </tr>
 <tr>
  <td class="padding14Top">Switch Name</td>
  <td  align="center" nowrap>
  <input type="text" name="switch_name" id="switch_name" value="LDLHome-Distribution" size="15" maxlength="20" onmousedown="enableImage();" onkeypress="enableImage();" />
 </td></tr>
 <tr>
  <td class="padding14Top">Serial Number</td>
  <td  align="center" nowrap>61W2015RA0357</td>
 </tr>
 <tr>
  <td class="padding14Top">MAC Address</td>
  <td  align="center" nowrap>BC:A5:11:B4:98:36</td>
 </tr>
 <tr>
  <td class="padding14Top">Bootloader Version</td>
  <td  align="center" nowrap>V1.6.0.2-VB</td>
 </tr>
 <tr>
  <td class="padding14Top">Firmware Version</td>
  <td  align="center" nowrap>V1.6.0.17</td>
 </tr>
 <tr>
  <td class="padding14Top">DHCP Mode</td>
  <td  align="center" nowrap>
  <select name="dhcpMode" id="dhcpMode" style="width:145px;" onchange="enableImage();dhcpModeChange();">
  <option value="0" selected>Disable</option>
  <option value="1">Enable</option>
  </select>
  <input type="checkbox" id="refresh" name="refresh" style="margin-left:5px;margin-right:5px;" disabled><span>Refresh</span>
  </td>
 </tr>
 <tr>
  <td class="padding14Top">IP Address</td>
  <td  align="center" nowrap>
  <input type="text" name="ip_address" id="ip_address" value="192.168.10.26" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
 <tr>
  <td class="padding14Top">Subnet Mask</td>
  <td  align="center" nowrap>
  <input type="text" name="subnet_mask" id="subnet_mask" value="255.255.255.0" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
 <tr>
  <td class="padding14Top">Gateway Address</td>
  <td  align="center" nowrap>
  <input type="text" name="gateway_address" id="gateway_address" value="192.168.10.254" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
<input type=hidden name='hash' id='hash' value="26957">
<input type=hidden name='err_msg' id='err_msg' value='' disabled>
 </table></td></tr>
</table></td></tr>
</table></form>
<script>
var str = CreateButtons('button','Cancel','javaScript:void(0)','btn_Cancel','off');
str += CreateButtons('button','Apply','javaScript:void(0)','btn_Apply','off');
PaintButtons(str);
</script>
</body>
</html>
