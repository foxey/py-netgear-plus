<!DOCTYPE html>
<html>
 <head>
 <title>Port Status</title>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/style.css?b1.6.0.9">
<script  src="/frame.js?b1.6.0.9" type="text/javascript"></script>
<script  src="/function.js?b1.6.0.9" type="text/javascript"></script>
</head>
<body onload="initTableCss()">
<form method="post" action="status.cgi">
<table class="detailsAreaContainer">
<tr>
<td><table class="tableStyle">
<tr>
<script>tbhdrTable('ss018','portStatus')</script>
</tr>
 
 
    <tr>
     <td class="paddingTableBody" colspan="2"><table class="tableStyle" id="tbl2" style="width:728px;">
      <tr><td class="def_TH spacer4Percent def_center"><input type="checkbox" name="checkALL" rownumber="" value="notchecked" onclick="checkAllCheckedRows('portID')" /></td>
         <td class="def_TH spacer7Percent">ss017</td>
         <td class="def_TH spacer20Percent">ss145</td>
      	<td class="def_TH" style="width:16;">ss018</td>
      	<td class="def_TH" style="width:16;">ss019</td>
      	<td class="def_TH spacer20Percent">ss020</td>
      	<td class="def_TH" style="width:16;">ss021</td>
      	<td class="def_TH spacer22Percent">ss146</td></tr>
      <tr id="g_1_1" exclusive="">
       <td class="def_TH def_center"></td>
       <td class="def_TH" sel="text"></td>
       <td class="def_TH" sel="input"><input type="text" name="DESCRIPTION" maxlength="32" style="padding:0px; height: 17px" disabled></td>
       <input type=hidden name='test' id='test' value="0">
       <td class="def_TH" sel="text"></td>
       <td class="def_TH" sel="select"><select name="SPEED" disabled>
        <option value="0"></option>
        <option value="1">ss024</option>
        <option value="2">ss013</option>
        <option value="3">10M half</option>
        <option value="4">10M full</option>
        <option value="5">100M half</option>
        <option value="6">100M full</option>
       </select>
       </td>
       <td class="def_TH" sel="text"></td>
       <td class="def_TH" sel="select"><select name="FLOW_CONTROL" disabled>
        <option value="0"></option>
        <option value="1">ss012</option>
        <option value="2">ss013</option>
       </select>
       </td>
       <td class="def_TH" sel="text"></td>      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port1" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">1
       <input type="hidden" value="1">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss022
       <input trans type="hidden" value="ss022">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">100M
       <input trans type="hidden" value="100M">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port2" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">2
       <input type="hidden" value="2">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port3" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">3
       <input type="hidden" value="3">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port4" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">4
       <input type="hidden" value="4">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port5" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">5
       <input type="hidden" value="5">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port6" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">6
       <input type="hidden" value="6">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port7" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">7
       <input type="hidden" value="7">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
      <tr class="portID"><td class="def firstCol def_center"><input class="checkbox" type="checkbox" name="port8" rownumber="" value="checked" onclick="checkBoxOnclick();"></td>
       <td class="def" sel="text">8
       <input type="hidden" value="8">
       </td>
<td untrans class="def" sel="input"></td>
       <td class="def" sel="text">ss023
       <input trans type="hidden" value="ss023">
       </td>
       <td class="def" sel="select">ss024
       <input type="hidden" value="1"></td>
       <td class="def" sel="text">ss027
       <input trans type="hidden" value="ss027">
       </td>
       <td class="def" sel="select">ss013
       <input type="hidden" value="2">
       </td>
       <td class="def firstCol" sel="text">16349
       <input type="hidden" value="16349">
</td>
      </tr>
<input type=hidden name='hash' id='hash' value="27414">
       </table>
      </td>
     </tr>
    </table>
   </td>
  </tr>
 </table>
</form>
<script>
var str = CreateButtons('button','bt03','refreshForm()','btn_Refresh','on');
str += CreateButtons('button','bt02','javaScript:void(0)','btn_Apply','off');
PaintButtons(str);
</script>
</body>
</html>
