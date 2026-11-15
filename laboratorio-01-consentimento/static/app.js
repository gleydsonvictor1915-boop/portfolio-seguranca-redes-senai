"use strict";
const chave="token_laboratorio_local";
const caixaConsentimento=document.querySelector("#consentimento");
const caixaTeste=document.querySelector("#teste");
const status=document.querySelector("#status");
function atualizarTela(){
  const consentiu=Boolean(sessionStorage.getItem(chave));
  caixaConsentimento.classList.toggle("oculto",consentiu);
  caixaTeste.classList.toggle("oculto",!consentiu);
}
async function enviar(rota,dados){
  const resposta=await fetch(rota,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(dados)});
  const resultado=await resposta.json();
  if(!resposta.ok){
    if(resposta.status===403){sessionStorage.removeItem(chave);atualizarTela();}
    throw new Error(resultado.erro||"Erro desconhecido");
  }
  return resultado;
}
document.querySelector("#aceitar").addEventListener("click",async()=>{
  try{
    const resultado=await enviar("/api/consentimento",{});
    sessionStorage.setItem(chave,resultado.token);
    status.textContent="Consentimento registrado. Agora você pode testar.";
    atualizarTela();
  }catch(erro){status.textContent="Falha: "+erro.message;}
});
document.querySelector("#registrar").addEventListener("click",async()=>{
  try{
    await enviar("/api/eventos",{token:sessionStorage.getItem(chave),tipo:"clique_botao_teste"});
    status.textContent="Clique registrado! Abra o painel para visualizar.";
  }catch(erro){status.textContent="Falha: "+erro.message;}
});
document.querySelector("#revogar").addEventListener("click",async()=>{
  try{
    await enviar("/api/revogar",{token:sessionStorage.getItem(chave)});
    status.textContent="Coleta interrompida.";
  }catch(erro){status.textContent="Falha: "+erro.message;}
  finally{sessionStorage.removeItem(chave);atualizarTela();}
});
atualizarTela();
