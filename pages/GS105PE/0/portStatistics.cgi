
<!DOCTYPE html>
<html>
<head>
<title>Port Statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/style.css?a1.6.0.14">
<script  src="/frame.js?a1.6.0.14" type="text/javascript"></script>
<script  src="/function.js?a1.6.0.14" type="text/javascript"></script>
</head>

<body onload="initTableCss();showCounter()">
<form method="post" action="portStatistics.cgi">
<input type="hidden" name="clearCounters" id="clearCounters" value="">
<input type=hidden name='hash' id='hash' value="32005">
</form>
<form method="get" action="portStatistics.cgi">
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdr('Port Statistics','portStatistics')</script>
</tr>
<tr><td class="topTitleBottomBar" colspan="2"></td></tr>
<tr><td class="paddingTableBody" colspan="2"><table class="tableStyle" id="tbl2" style='width:728px;'>
<tr>
<tr><td class="def_TH">Port</td>
<td class="def_TH spacer30Percent">Bytes Received</td>
<td class="def_TH spacer30Percent">Bytes Sent</td>
<td class="def_TH spacer30Percent">CRC Error Packets</td></tr>
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">1</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="1343">
<input type="hidden" value="4015730058">
<td class="def" sel="text">4015730058
</td>
<input type="hidden" value="1182">
<input type="hidden" value="3595230089">
<td class="def" sel="text">3595230089
</td>
<input type="hidden" value="0">
<input type="hidden" value="7">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">2</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="287">
<input type="hidden" value="4214080008">
<td class="def" sel="text">4214080008
</td>
<input type="hidden" value="28">
<input type="hidden" value="744086718">
<td class="def" sel="text">744086718
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">3</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<td class="def" sel="text">0
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<td class="def" sel="text">0
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">4</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="940">
<input type="hidden" value="1413899239">
<td class="def" sel="text">1413899239
</td>
<input type="hidden" value="472">
<input type="hidden" value="852542720">
<td class="def" sel="text">852542720
</td>
<input type="hidden" value="0">
<input type="hidden" value="0">
<tr class="portID" name="portID">
<td class="def firstCol" sel="text">5</td>
<td class="def" sel="text">
</td>
<input type="hidden" value="1624">
<input type="hidden" value="2828228358">
<td class="def" sel="text">2828228358
</td>
<input type="hidden" value="2573">
<input type="hidden" value="2291979244">
<td class="def" sel="text">2291979244
</td>
<input type="hidden" value="0">
<input type="hidden" value="155091">
</tr>
</table>
</td></tr>
</table>
</td></tr>
</form>
<script>
var str = CreateButtons('button','Clear Counters','submitClearCounters()','btn_Cancel','on');
str += CreateButtons('button','Refresh','submitForm()','btn_Refresh','on');
PaintButtons(str);
</script>
</body>
</html>
