import pandas as pd
import math

def _parse_float(value):
    if pd.isna(value):
        return float('nan')
    try:
        return float(str(value).replace(',', '.').strip())
    except:
        return float('nan')

df = pd.read_excel('preciosEESS_es.xls', engine='xlrd', header=3)
df.columns = df.columns.str.strip()

for col in ['Latitud', 'Longitud']:
    df[col] = df[col].apply(_parse_float)

precio_cols = [c for c in df.columns if c.strip().lower().startswith('precio')]
for col in precio_cols:
    df[col] = df[col].apply(_parse_float)

df = df.dropna(subset=['Latitud','Longitud'])
df = df[df['Latitud'].between(-90,90) & df['Longitud'].between(-180,180)]

print(f'Total estaciones: {len(df)}')

col_precio_95 = 'Precio gasolina 95 E5'
col_rotulo = next((c for c in df.columns if 'tulo' in c.lower()), None)
col_dir = next((c for c in df.columns if 'irecci' in c.lower()), None)
print(f'Col precio 95 encontrada: {col_precio_95 in df.columns}')
print(f'Col rotulo: {repr(col_rotulo)}')
print(f'Col dir: {repr(col_dir)}')

def haversine(lat1,lon1,lat2,lon2):
    R=6371
    phi1,phi2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1)
    dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return R*2*math.asin(math.sqrt(a))

lat,lon=40.4168,-3.7038
sub = df[df[col_precio_95].notna() & (df[col_precio_95]>0)].copy()
sub['dist'] = sub.apply(lambda r: haversine(lat,lon,r['Latitud'],r['Longitud']),axis=1)
sub = sub[sub['dist']<=10].sort_values(col_precio_95).head(5)
print()
print(sub[[col_rotulo, 'Municipio', col_precio_95, 'dist']].to_string())
