<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="format-detection" content="telephone=no,email=no,address=no">
<link rel="stylesheet" type="text/css" href="login.css?v=V1.6.0.30">
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgo=">
<title>NETGEAR XS716E</title>
<script src="XS716E/login.js?v=V1.6.0.30" type="text/javascript"></script>
<script src="XS716E/function.js?v=V1.6.0.30" type="text/javascript"></script>
<script src="XS716E/login_en.js?v=V1.6.0.30" type="text/javascript"></script>
<script language="JavaScript">
function submitLogin()
{
	CalcMD5PW();
	
	document.forms[0].elements.passwordP.disabled = true;
	document.forms[0].submit();
	return true;
}
function CalcMD5PW()
{
  var count    = 0;
  var space    = "\0";
  var md5Key   = "YOU_CAN_NOT_PASS";
  var password = document.forms[0].elements.passwordP.value;
  var passwrd;
  var encryPw;

  while (count <= (2048 - (password.length + 1))) {
    if (count === 0) {
      passwrd = password;
    } else {
      passwrd += password;
    }
    passwrd += space;
    count += (password.length + 1);
  }

  while (count < 2048) {
    passwrd += space;
    count += 1;
  }

  encryPw = hex_hmac_md5(md5Key, passwrd);

  document.forms[0].elements.password.value = encryPw;
}
function showErrmsg()
{
	var errMsg = document.getElementById("err_msg");
	var errDiv = document.getElementById("pwdErr");

	if (errMsg.value != "")
	{
		errDiv.innerHTML = errMsg.value;
	}
	else
	{
		errDiv.innerHTML = "";
	}
}
</script>
</head>
<body onload="init(); showErrmsg(); changeLoginButtonStyle();">
<div id="mainArea" class="mainArea" style="display:none">
  <div id="mainTitleArea" class="mainTitleArea">
   <img class="customGraph" src="NgrLogo.png">
   <img class="factGraph" src="ContentVisual.png">
   <div class="switchInfo">XS716E<script>document.write(loginStr0006 + "16" + loginStr0007)</script></div>
  </div>
  <div id="loginContainer" class="loginContainer">
   <form method="post" action="login.cgi" name="login" autocomplete="off">
   <input type=hidden name='csrftoken' id='csrftoken' value='13095'>
    <div id="contentArea">
	 <div id="loginArea" class="loginArea">
	  <div id="loginTitleArea">
	   <table>
		<tr>
		<script>tbhdrLoginTable(loginStr0001,'login');</script>
		</tr>
		<tr>
		 <td></td>
		 <td colspan="2">
		  <table>
		   <tr>
		    <td class="topLoginTitleBottomBar"></td>
		   </tr>
		  </table>
		 </td>
		 <td></td>
		</tr>
	   </table>
	  </div>
	  <div id="loginBlkbArea" class="bClass">
	   <div id="loginDiv" class="loginBox">
	    <div id="loginTDataArea" class="tableData mTop25">
	     <table id="loginTData">
	      <tbody>
	       <tr>
		  <td width="23px"><div></div></td>
		  <td width="100px">
		   <div class="colInterval textLeft"><span id="login_password"><script>document.write(loginStr0002)</script></span></div>
		  </td>
		  <td width="290px">
		   <input id="passwordP" class="textInputStyle textInputLength" type="password" name="passwordP" maxlength="20" style="border:1px #CCCCCC solid;" onkeypress="if (event.keyCode == 13) {submitLogin();}">
		  </td>
		  <td width="23px"><div></div></td>
              </tr>
              <tr>
		  <td width="23px"><div></div></td>
		  <td width="100px"><div></div></td>
		  <td width="290px">
		   <div id="pwdErr" class="pwdErrStyle"></div>
		  </td>
		  <td width="23px"><div></div></td>
		</tr>
 			 <tr>
 			  <td width="23px"><div></div></td>
 			  <td width="100px"><div></div></td>
 			  <td width="290px">
 			   <a id="loginBtn" href="javascript:submitLogin()"><span class="loginBtnStyle" id="login_login"><script>document.write(loginStr0001)</script></span></a>
 			  </td>
 			  <td width="23px"><div></div></td>
 			 </tr>
 			</tbody>
 		   </table>
 		  </div></div></div></div></div>
 		  <input type=hidden name='err_msg' id='err_msg' value="" disabled>
 		  <input type=hidden name='password' id='password'>
 		 </form>
 		</div>
         <div class="footerImg">
          <div class="copyrightGraphWrap">
           <span id="login_copy_right"><script>document.write(loginStr0003)</script></span>
          </div>
          <img style="float:right;" src="Footer_Facet.png">
         </div>
  </div>
<script>
if(typeof(loginLangReady)=="undefined" || typeof(loginJsReady)=="undefined" || typeof(funcJsReady)=="undefined")
	location.reload();
else
	document.getElementById("mainArea").style.display="";
</script>
</body>
</html>
