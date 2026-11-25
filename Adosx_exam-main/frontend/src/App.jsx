import {useEffect,useState} from 'react'
const reasons=['MISSING_IN_B','ORPHAN_IN_B','DUPLICATE_IN_B','VALUE_MISMATCH','INVALID_AMOUNT','VOIDED_ENTRY_IN_B','LOCATION_MISMATCH','DATE_MISMATCH']
export default function App(){
 const [org,setOrg]=useState('ORG-A'),[reason,setReason]=useState(''),[sort,setSort]=useState(''),[data,setData]=useState({results:[],summary:{}}),[err,setErr]=useState('')
 useEffect(()=>{const p=new URLSearchParams({org});if(reason)p.set('reason',reason);if(sort)p.set('sort',sort);fetch('/api/disagreements/?'+p).then(r=>{if(!r.ok)throw Error('API '+r.status);return r.json()}).then(setData).catch(e=>setErr(e.message))},[org,reason,sort])
 return <main><header><div><small>DEALEROS / DATA QUALITY</small><h1>Reconciliation report</h1><p>Compare ledger events across System A and System B.</p></div><label>Organization<select value={org} onChange={e=>setOrg(e.target.value)}><option>ORG-A</option><option>ORG-B</option></select></label></header>
 <section className="summary"><b>{data.summary?.total||0}</b> disagreements {Object.entries(data.summary?.by_reason||{}).map(([k,v])=><span key={k}>{k}: {v}</span>)}</section>
 <label>Reason filter<select value={reason} onChange={e=>setReason(e.target.value)}><option value="">All reasons</option>{reasons.map(r=><option key={r}>{r}</option>)}</select></label>
 {err&&<p className="error">{err}. Ensure Django is running.</p>}
 {data.results?.length?<div className="table"><table><thead><tr>{['Reason','Record ID','Location','System A value'].map(x=><th key={x}>{x}</th>)}<th><button onClick={()=>setSort(s=>s==='-value'?'value':'-value')}>System B value ↕</button></th><th>Difference</th><th>Details</th></tr></thead><tbody>{data.results.map((r,i)=><tr key={r.reason+r.record_id+i}><td>{r.reason}</td><td>{r.record_id}</td><td>{r.location||''}</td><td>{r.a_value??''}</td><td>{r.b_value??''}</td><td>{r.difference??''}</td><td>{r.details}</td></tr>)}</tbody></table></div>:<p className="empty">No disagreements found for this selection.</p>}</main>
}
