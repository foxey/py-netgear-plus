<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>Switch Information</title>
<link rel="stylesheet" type="text/css" href="/style.css?b1.6.0.9">
<script src="/frame.js?b1.6.0.9" type="text/javascript"></script>
<script src="/function.js?b1.6.0.9" type="text/javascript"></script>
<script language="JavaScript">
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
	popUpWindown('alert','ss011','ms15');
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
<body onload="initErrMsg('ss007');selectOptions();">
<form method="post" action="/switch_info.cgi">
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdrTable('ss007', 'switchInformation');</script>
</tr>
<tr><td class="paddingTableBody" colspan='2'><table class="tableStyle" id="tbl2" style="width:728px;">
 <tr>
  <td width='300' class="padding14Top">ss008</td>
  <td align="center" nowrap>GSS108E</td>
 </tr>
 <tr>
  <td class="padding14Top">ss094</td>
  <td  align="center" nowrap>
  <input untrans type="text" name="switch_name" id="switch_name" value="WOHNZIMMER" size="15" maxlength="20" onmousedown="enableImage();" onkeypress="enableImage();" />
 </td></tr>
 <tr>
  <td class="padding14Top">ss091</td>
  <td  align="center" nowrap>4852615902565</td>
 </tr>
 <tr>
  <td class="padding14Top">ss009</td>
  <td  align="center" nowrap>B0:7F:B9:38:06:57</td>
 </tr>
 <tr>
  <td class="padding14Top">ss010</td>
  <td  align="center" nowrap>V1.6.0.9</td>
 </tr>
 <tr>
  <td class="padding14Top">ss011</td>
  <td  align="center" nowrap>
  <select name="dhcpMode" id="dhcpMode" style="width:145px;" onchange="enableImage();dhcpModeChange();">
  <option value="0" selected>ss013</option>
  <option value="1">ss012</option>
  </select>
  <input type="checkbox" id="refresh" name="refresh" style="margin-left:5px;" disabled><span>bt03</span>
  </td>
 </tr>
 <tr>
  <td class="padding14Top">ss014</td>
  <td  align="center" nowrap>
  <input type="text" name="ip_address" id="ip_address" value="192.168.178.251" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
 <tr>
  <td class="padding14Top">ss015</td>
  <td  align="center" nowrap>
  <input type="text" name="subnet_mask" id="subnet_mask" value="255.255.255.0" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
 <tr>
  <td class="padding14Top">ss016</td>
  <td  align="center" nowrap>
  <input type="text" name="gateway_address" id="gateway_address" value="192.168.178.254" size="15" maxlength="15" onmousedown="enableImage();" onkeypress="enableImage();">
  </td>
 </tr>
<input type=hidden name='hash' id='hash' value="27414">
<input type=hidden name='err_msg' id='err_msg' value='' disabled>
 </table></td></tr>
</table></td></tr>
</table></form>
<script>
var str = CreateButtons('button','bt01','javaScript:void(0)','btn_Cancel','off');
str += CreateButtons('button','bt02','javaScript:void(0)','btn_Apply','off');
PaintButtons(str);
</script>
</body>
</html>
