
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css" href="/login.css?a1.6.0.14">
<title>NETGEAR GS105PE</title>
<script src="/jquery.md5.js?a1.6.0.14" type="text/javascript"></script>
<script src="/login.js?a1.6.0.14" type="text/javascript"></script>
<script language="JavaScript">
function submitLogin()
{
    encryptPwd();
	document.forms[0].submit();
	return true;
}
</script>
</head>
<body onload="init();changeLoginButtonStyle();">
<div id="mainArea" class="mainArea">
  <div id="mainTitleArea" class="mainTitleArea">
   <img class="customGraph" src="/CBU_NgrLogo.png">
   <img class="factGraph" src="/CBU_IMG_ContentVisual.png">
   <div class="switchInfo">GS105PE &ndash; 5-Port Gigabit Ethernet Smart Managed Plus Switch (PoE Pass-Thru)</div>
  </div>
  <div id="loginContainer" class="loginContainer">
   <form method="post" action="/login.cgi" name="login" onSubmit="return false;">
   <input id="submitPwd" name="password" type="hidden" value="">
    <div id="contentArea">
	 <div id="loginArea" class="loginArea">
	  <div id="loginTitleArea">
	   <table>
		<tr>
		<script>tbhdrLoginTable('Login','login');</script>
		</tr>
		<tr>
		 <td colspan="2">
		  <table>
		   <tr>
		    <td class="topLoginTitleBottomBar"></td>
		   </tr>
		  </table>
		 </td>
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
		  <td width="100px" style='white-space:nowrap'>
		   <div class="colInterval textLeft">Password</div>
		  </td>
		  <td width="290px">
		   <input id="password" class="textInputStyle textInputLength" onkeypress="onEnterSub(event);" type="password" maxlength="20" style="border:1px #CCCCCC solid;" autocomplete="off">
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
                 <a id="loginBtn" class="loginBtnStyle" href="javascript:submitLogin()">Login</a>
               </td>
               <td width="23px"><div></div></td>
             </tr>
           </tbody>
         </table>
       </div></div></div></div></div>
       <input type=hidden id='rand' value='2036145558' disabled>     </form>
   </div>
         <div class="footerImg">
          <div class="copyrightGraphWrap">
           <span>&copy; NETGEAR, Inc. All rights reserved.</span>
          </div>
          <img style="float:right;" src="/Footer_Facet_Graphic.png">
         </div>
  </div>
</body>
</html>
