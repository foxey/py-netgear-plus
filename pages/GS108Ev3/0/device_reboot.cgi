<!DOCTYPE HTML>
<html>
<head>
<title>Device Reboot</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="stylesheet" type="text/css" href="style.css?v1.10">
<script src="frame.js?v1.10" type="text/javascript"></script>
<script src="function.js?v1.10" type="text/javascript"></script>
<script language="JavaScript">
function doReload()
{
	var url = window.location.href;
	if (url.indexOf('/device_reboot.cgi') != -1)
	{
		top.location.href = url.substring(0, url.lastIndexOf('/device_reboot.cgi'));
	}
	else
	{
		alert("Refresh to reload.");
	}
}
function reloadAll()
{
		setTimeout("doReload();", 6000);
}
</script>
</head>
<body>
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdr('Device Reboot','deviceReboot')</script>
</tr><tr><td class="topTitleBottomBar" colspan='2'></td></tr>
<tr><td class="paddingsubSectionBodyNone" colspan='2'><table class="tableStyle" style="width:745px;">
 <tr>
	<td colspan='2'>Check box and click Apply button to reboot switch.
	<input type="checkbox" name="CBox" id="CBox" alue="0" style="margin-left:25px;" onclick="buttonsChange();" checked>
	</td>
 </tr>
</table>
 </td>
</tr>
</table>
</td></tr>
</table>
<script>
var str = CreateButtons('button','Cancel','javaScript:void(0)','btn_Cancel','off');
str += CreateButtons('button','Apply','javaScript:void(0)','btn_Apply','off');
PaintButtons(str);
popUpWindown('alert', 'Device Reboot', 'The device is restarting. Wait until the process is complete.', true);
reloadAll();
</script>
</body>
</html>
