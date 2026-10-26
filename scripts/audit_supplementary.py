"""Financial data are injection-only; HoloClean long references are not wide tables."""
import csv,hashlib,io,json,pathlib,zipfile,collections
import xlrd
root=pathlib.Path('.');manifest=json.loads((root/'manifests/files.json').read_text());out={}
for p in (root/'data/recovery_downloads').glob('*.zip'):
 url='https://archive.ics.uci.edu/static/public/'+('350/' if 'credit' in p.name else '222/')+p.name
 manifest.append(dict(repository='UCI',revision='archive version not stated; content pinned by SHA-256',source_path=p.name,path=str(p),url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rights='UCI dataset pages describe CC BY 4.0; no downstream error label rights implied',state='FULL_ARCHIVE_ACQUIRED'))
 with zipfile.ZipFile(p) as z:
  out[p.name]={'members':z.namelist(),'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'error_labels':'NONE; outcome not DQ label'}
  target=root/'data/derived/uci';target.mkdir(parents=True,exist_ok=True)
  if 'credit' in p.name:
   name=next(x for x in z.namelist() if x.endswith('.xls'));book=xlrd.open_workbook(file_contents=z.read(name));sheet=book.sheet_by_index(0);rows=[sheet.row_values(i) for i in range(2,sheet.nrows)]
   out[p.name].update(shape=[len(rows),sheet.ncols],columns=sheet.row_values(1),id_unique=len({x[0] for x in rows})==len(rows),duplicate_feature_rows=len(rows)-len({tuple(x[1:-1]) for x in rows}),empty_cells=sum(x=='' for row in rows for x in row),sheet=sheet.name,member=name,member_sha256=hashlib.sha256(z.read(name)).hexdigest())
  else:
   for member in z.namelist():
    if member.endswith('bank-additional.zip'):
     with zipfile.ZipFile(io.BytesIO(z.read(member))) as inner:
      name=next(x for x in inner.namelist() if x.endswith('bank-additional-full.csv'));b=inner.read(name);reader=csv.reader(io.StringIO(b.decode()),delimiter=';');h=next(reader);rows=list(reader)
      out[p.name].update(shape=[len(rows),len(h)],columns=h,duplicate_feature_rows=len(rows)-len({tuple(x[:-1]) for x in rows}),empty_cells=sum(x=='' for row in rows for x in row),literal_unknown=sum(x=='unknown' for row in rows for x in row),member=member+'!'+name,member_sha256=hashlib.sha256(b).hexdigest())
# Explicit HoloClean long-key audit, without fabricating wide clean files.
for name in ['hospital','flight']:
 p=root/'data/raw/HoloClean__holoclean/testdata';h,d=__import__('thesis_audit.audit',fromlist=['read_table']).read_table(p/(name+'.csv'))
 hc,c=__import__('thesis_audit.audit',fromlist=['read_table']).read_table(p/(name+'_clean.csv'))
 keys=collections.Counter((x[0],x[1]) for x in c)
 details={'dirty_shape':[len(d),len(h)],'reference_shape':[len(c),len(hc)],'reference_schema':hc,'dirty_schema':h,'duplicate_reference_keys':sum(v-1 for v in keys.values()),'unknown_attributes':sorted({x[1] for x in c}-set(h))}
 if name=='hospital':
  details.update(key_type='zero-based row tid + attribute',tid_range=[min(int(x[0]) for x in c),max(int(x[0]) for x in c)],coverage=len(keys)/(len(d)*len(h)))
  from thesis_audit.audit import read_table
  rh,rd=read_table(root/'data/raw/BigDaMa__raha/datasets/hospital/dirty.csv')
  rch,rc=read_table(root/'data/raw/BigDaMa__raha/datasets/hospital/clean.csv')
  ref={(int(x[0]),x[1]):x[2] for x in c}
  details['raha_dirty_equal_ignoring_index']=all(a==b[1:] for a,b in zip(d,rd)) and len(d)==len(rd)
  details['raha_dirty_equal_after_explicit_empty_sentinel_mapping']=all([v if v!='' else 'empty' for v in a]==b[1:] for a,b in zip(d,rd)) and len(d)==len(rd)
  details['raha_clean_matching_after_empty_mapping']=sum((ref.get((i,col)) or 'empty')==row[j+1] for i,row in enumerate(rc) for j,col in enumerate(h))
  details['raha_clean_matching_cells']=sum(ref.get((i,col))==row[j+1] for i,row in enumerate(rc) for j,col in enumerate(h))
 else:
  j=h.index('flight');entities={row[j] for row in d}
  details.update(key_type='flight entity identifier + attribute, NOT integer row tid',entity_count=len(entities),reference_entities=len({x[0] for x in c}),reference_entities_absent_from_dirty=len({x[0] for x in c}-entities),alignment_status='ENTITY_JOIN_REQUIRED; not interchangeable with Raha row reference')
 out['holoclean_'+name]=details

# Deduplicate manifest by path; a repeat does not add entries.
(root/'manifests/files.json').write_text(json.dumps(list({x['path']:x for x in manifest}.values()),indent=2)+'\n')
(root/'evidence/supplementary_audits.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
