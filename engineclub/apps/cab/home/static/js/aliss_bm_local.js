var t;
try {
 t= ((window.getSelection && window.getSelection()) ||
 (document.getSelection && document.getSelection()) ||
 (document.selection && 
 document.selection.createRange && 
 document.selection.createRange().text));
}
catch(e){ // access denied on https sites
 t = "";
}
var x = new String(t);
x = x.replace(/\n/g, "||");
var w=window.open('http://127.0.0.1:8080/depot/resource/add/popup|true/title|'+encodeURIComponent(document.title)+'/page|'+encodeURIComponent(location.href)+'/t|'+encodeURIComponent(x),'ALISS','scrollbars=1,status=0,resizable=1,location=0,toolbar=0,width=860,height=680');
//var w=window.open('http://127.0.0.1:8080/depot/resource/add/?popup=true&title='+encodeURIComponent(document.title)+'&page='+encodeURIComponent(location.href)+'&t='+encodeURIComponent(x),'ALISS','scrollbars=1,status=0,resizable=1,location=0,toolbar=0,width=860,height=680');
