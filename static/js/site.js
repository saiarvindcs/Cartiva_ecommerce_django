function csrfToken(){return document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]||''}
async function api(url, options={}){
 const token=sessionStorage.getItem('access_token');
 const headers={...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(token?{'Authorization':'Bearer '+token}:{}),...(csrfToken()?{'X-CSRFToken':decodeURIComponent(csrfToken())}:{}),...(options.headers||{})};
 const response=await fetch(url,{credentials:'same-origin',...options,headers});
 if(response.status===204)return null;
 const data=await response.json().catch(()=>({detail:'Unexpected server response'}));
 if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data));
 return data;
}
async function loginDemo(username,password){const result=await api('/api/auth/token/',{method:'POST',body:JSON.stringify({username,password})});sessionStorage.setItem('access_token',result.access);return result}
function logoutDemo(){sessionStorage.removeItem('access_token');location.href='/'}
async function updateAuthNavigation(){
 const token=sessionStorage.getItem('access_token');let me=null;
 if(token){try{me=await api('/api/accounts/me/')}catch(e){sessionStorage.removeItem('access_token')}}
 document.querySelectorAll('[data-guest]').forEach(el=>el.hidden=Boolean(me));
 document.querySelectorAll('[data-user]').forEach(el=>el.hidden=!me);
 document.querySelectorAll('[data-seller]').forEach(el=>el.hidden=!(me&&(me.role==='seller'||me.role==='admin')));
 document.querySelectorAll('[data-admin]').forEach(el=>el.hidden=!(me&&me.role==='admin'));

}
document.addEventListener('DOMContentLoaded',()=>{updateAuthNavigation();document.getElementById('logout-button')?.addEventListener('click',logoutDemo)});
function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

// Close the account popover when clicking elsewhere or pressing Escape.
document.addEventListener('click',e=>{const menu=document.querySelector('.account-menu');if(menu?.open&&!menu.contains(e.target))menu.open=false});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const menu=document.querySelector('.account-menu');if(menu)menu.open=false}});
