import pandas as pd
from tabulate import tabulate  # Importar la librería tabulate
import json


# Es importante colocar la ruta de los archivos de la prueba
ruta_base = r""

# Se me presento un error en la lectura de los archivos
#por lo cual utilice 'latin1'
empresa_df = pd.read_csv(ruta_base + r"\Empresa.csv", sep=';', encoding='latin1')
persona_df = pd.read_csv(ruta_base + r"\Persona.csv", sep=';', encoding='latin1')
consumo_df = pd.read_csv(ruta_base + r"\Consumo.csv", sep=';', encoding='latin1')

# converti la columna "valores" a string 
consumo_df['Valor'] = consumo_df['Valor'].astype(str).str.replace(',', '.').astype(float)

# realice la agrupación de "periodo, ues, producto" 
ventas_por_periodo = consumo_df.groupby(['Periodo', 'UES', 'Producto'])['Valor'].sum().reset_index()

# Como realice la combinación, necesito el valor máximo para cada combinación de productos 
indices_maximos = ventas_por_periodo.groupby(['Periodo', 'UES'])['Valor'].idxmax()

# necesito filtrar las filas solo las que contienen el valor maximo 
ventas_maximas_por_periodo = ventas_por_periodo.loc[indices_maximos]

# Ordenar los resultados por 'Periodo' y 'UES'
ventas_maximas_por_periodo = ventas_maximas_por_periodo.sort_values(by=['Periodo', 'UES'])

# Comverir en formato moneda 
ventas_maximas_por_periodo['Valor'] = ventas_maximas_por_periodo['Valor'].map(lambda x: f"${x:,.2f}")

print("¿Existen temporadas de mayor venta de productos?")
# Mostrar los resultados sin la numeración de filas
print(ventas_maximas_por_periodo.to_string(index=False))

print("¿Cuál es el consumo total por unidad de negocio?")

# Agrupar por 'UES' y sumarizar las ventas (consumo total por UES)
consumo_total_por_ues = consumo_df.groupby('UES')['Valor'].sum().reset_index()

# Comverir en formato moneda
consumo_total_por_ues['Valor'] = consumo_total_por_ues['Valor'].map(lambda x: f"${x:,.2f}")

# Quite la numeración de las filas
print("Estos son los valores de las unidades de negocio (UES):")
print(consumo_total_por_ues.to_string(index=False))

print("cual es la participación de consumo de personas afiliadas y no afiliadas")
# Manejar UES en blanco: reemplazar con "SIN UES"
consumo_df['UES'] = consumo_df['UES'].fillna("SIN UES")

# Identificar personas afiliadas y no afiliadas
# Personas afiliadas: están en consumo_df y en persona_df
personas_afiliadas = consumo_df[consumo_df['NumIdPersona'].isin(persona_df['NumIdPersona'])]['NumIdPersona'].unique()
# Personas no afiliadas: están en consumo_df pero no en persona_df
personas_no_afiliadas = consumo_df[~consumo_df['NumIdPersona'].isin(persona_df['NumIdPersona'])]['NumIdPersona'].unique()

# Calcular el total de personas únicas en consumo_df
total_personas_consumo = consumo_df['NumIdPersona'].nunique()

# Realizamos la fomula de 3 para calcular afiliados y no afiliados %
porcentaje_afiliadas = (len(personas_afiliadas) / total_personas_consumo) * 100
porcentaje_no_afiliadas = (len(personas_no_afiliadas) / total_personas_consumo) * 100

# Resultados de afiliados y no afiliados 
print(f"Porcentaje de personas afiliadas que consumieron: {porcentaje_afiliadas:.2f}%")
print(f"Porcentaje de personas no afiliadas que consumieron: {porcentaje_no_afiliadas:.2f}%")

# Filtrar solo personas afiliadas (que están en persona_df)
personas_afiliadas = persona_df['NumIdPersona'].unique()

# Filtrar consumos de personas afiliadas
consumos_afiliados = consumo_df[consumo_df['NumIdPersona'].isin(personas_afiliadas)]

# total de personas afiliadas únicas que realizaron consumo
total_afiliados_consumo = consumos_afiliados['NumIdPersona'].nunique()

# porcentaje de afiliados que compraron productos por cada UES
ues_unicas = consumos_afiliados['UES'].unique()
print("\nPorcentaje de personas afiliadas que compraron productos por UES:")
for ues in ues_unicas:
    # Filtrar consumos de esta UES para afiliados
    consumos_ues_afiliados = consumos_afiliados[consumos_afiliados['UES'] == ues]
    num_afiliados_ues = consumos_ues_afiliados['NumIdPersona'].nunique()
    
    # Calcular el porcentaje respecto al total de afiliados que realizaron consumo
    porcentaje_afiliados_ues = (num_afiliados_ues / total_afiliados_consumo) * 100
    print(f"UES {ues}: {porcentaje_afiliados_ues:.2f}%")

# porcentaje de personas afiliadas que no realizaron consumo
personas_afiliadas_sin_consumo = persona_df[~persona_df['NumIdPersona'].isin(consumo_df['NumIdPersona'])]['NumIdPersona'].unique()
num_afiliados_sin_consumo = len(personas_afiliadas_sin_consumo)
total_afiliados = persona_df['NumIdPersona'].nunique()
porcentaje_afiliados_sin_consumo = (num_afiliados_sin_consumo / total_afiliados) * 100

# Resultados de acuerdo al calculo
print(f"\nPorcentaje de personas afiliadas que no realizaron consumo: {porcentaje_afiliados_sin_consumo:.2f}%")

print("¿Cuáles son las unidades y productos de mayor uso en cada categoría??")

# agrupamos UES y Producto, y contar la frecuencia
uso_por_ues_producto = consumo_df.groupby(['UES', 'Producto']).size().reset_index(name='Frecuencia')

# total total de registros por UES
total_por_ues = consumo_df.groupby('UES').size().reset_index(name='Total_UES')

# DataFrames para calcular el porcentaje de frecuencia por UES
uso_por_ues_producto = pd.merge(uso_por_ues_producto, total_por_ues, on='UES', how='left')
uso_por_ues_producto['% Mayor-Uso'] = (uso_por_ues_producto['Frecuencia'] / uso_por_ues_producto['Total_UES']) * 100

# Redondear a 3 decimales
uso_por_ues_producto['% Mayor-Uso'] = uso_por_ues_producto['% Mayor-Uso'].round(3)

# Identificar el producto más usado por cada UES, solo dejar valores unicos.
uso_por_ues_producto_sorted = uso_por_ues_producto.sort_values(by='Frecuencia', ascending=False)
producto_mas_usado_por_ues = uso_por_ues_producto_sorted.drop_duplicates(subset=['UES'])

#salida como una tabla
tabla_resultados = producto_mas_usado_por_ues[['UES', 'Producto', '% Mayor-Uso']]
tabla_resultados.columns = ['UES', 'Producto', '% Mayor-Uso'] 

# Mostrar la tabla
print(tabulate(tabla_resultados, headers='keys', tablefmt='pretty', showindex=False))

print ("Identifique los clientes (afiliados y no afiliados) con mayor frecuencia de uso y mayor valor neto de venta.")

# Identificar si un cliente es afiliado o no afiliado
consumo_df['Tipo_Cliente'] = consumo_df['NumIdPersona'].isin(persona_df['NumIdPersona']).map({True: 'Afiliado', False: 'No Afiliado'})

# Calcular la frecuencia de uso y el valor neto de venta por cliente
clientes_analisis = consumo_df.groupby(['NumIdPersona', 'Tipo_Cliente']).agg(
    Frecuencia=('Valor', 'size'), 
    Valor_Neto=('Valor', 'sum')   
).reset_index()

# Identificar los clientes con mayor frecuencia de uso
clientes_mayor_frecuencia = clientes_analisis.sort_values(by='Frecuencia', ascending=False).head(30)

# Identificar los clientes con mayor valor neto de venta
clientes_mayor_valor = clientes_analisis.sort_values(by='Valor_Neto', ascending=False).head(30)

# convertir valor en moneda
clientes_mayor_frecuencia['Valor_Neto'] = clientes_mayor_frecuencia['Valor_Neto'].map(lambda x: f"${x:,.2f}")
clientes_mayor_valor['Valor_Neto'] = clientes_mayor_valor['Valor_Neto'].map(lambda x: f"${x:,.2f}")

# Mistrar los reultados
print("Clientes con mayor frecuencia de uso:")
print(tabulate(clientes_mayor_frecuencia, headers='keys', tablefmt='pretty', showindex=False))

print("\nClientes con mayor valor neto de venta (ordenados de mayor a menor):")
print(tabulate(clientes_mayor_valor, headers='keys', tablefmt='pretty', showindex=False))

print ("¿Cómo ha sido el porcentaje histórico de penetración en la población afiliada de los servicios Colsubsidio?")

# Identificar afiliados y no afiliados
consumo_df['Tipo_Cliente'] = consumo_df['NumIdPersona'].isin(persona_df['NumIdPersona']).map({True: 'Afiliado', False: 'No Afiliado'})

# Contar el número de afiliados y no afiliados que realizaron transacciones por período
transacciones_por_periodo = consumo_df.groupby(['Periodo', 'Tipo_Cliente'])['NumIdPersona'].nunique().reset_index()
transacciones_por_periodo.columns = ['Periodo', 'Tipo_Cliente', 'Clientes_Con_Consumo']

# total de afiliados y no afiliados en todos los períodos
total_afiliados = transacciones_por_periodo[transacciones_por_periodo['Tipo_Cliente'] == 'Afiliado']['Clientes_Con_Consumo'].sum()
total_no_afiliados = transacciones_por_periodo[transacciones_por_periodo['Tipo_Cliente'] == 'No Afiliado']['Clientes_Con_Consumo'].sum()

# porcentaje de penetración para afiliados y no afiliados
transacciones_por_periodo.loc[transacciones_por_periodo['Tipo_Cliente'] == 'Afiliado', 'Porcentaje_Penetracion'] = (
    transacciones_por_periodo.loc[transacciones_por_periodo['Tipo_Cliente'] == 'Afiliado', 'Clientes_Con_Consumo'] / total_afiliados) * 100
transacciones_por_periodo.loc[transacciones_por_periodo['Tipo_Cliente'] == 'No Afiliado', 'Porcentaje_Penetracion'] = (
    transacciones_por_periodo.loc[transacciones_por_periodo['Tipo_Cliente'] == 'No Afiliado', 'Clientes_Con_Consumo'] / total_no_afiliados) * 100

# simplificar los resultados.
transacciones_por_periodo['Porcentaje_Penetracion'] = transacciones_por_periodo['Porcentaje_Penetracion'].round(2)

# Numero de comprar por periodo
transacciones_por_periodo['Clientes_Con_Consumo'] = transacciones_por_periodo['Clientes_Con_Consumo'].apply(lambda x: f"{x:,.0f}")

#Se muestra en una tabla el periodo, clientes consumo, porcentaje
afiliados_por_periodo = transacciones_por_periodo[transacciones_por_periodo['Tipo_Cliente'] == 'Afiliado']
no_afiliados_por_periodo = transacciones_por_periodo[transacciones_por_periodo['Tipo_Cliente'] == 'No Afiliado']

print(tabulate(afiliados_por_periodo[['Periodo', 'Clientes_Con_Consumo', 'Porcentaje_Penetracion']],
               headers=['Periodo', 'Afiliados con Consumo', 'Porcentaje (%)'],
               tablefmt='pretty', showindex=False))

print(tabulate(no_afiliados_por_periodo[['Periodo', 'Clientes_Con_Consumo', 'Porcentaje_Penetracion']],
               headers=['Periodo', 'No Afiliados con Consumo', 'Porcentaje (%)'],
               tablefmt='pretty', showindex=False))

print ("¿Cuáles son los productos más consumidos en el cada segmento poblacional? ")

# se anida personas y grupo poblacional 
consumo_con_segmento = pd.merge(consumo_df, persona_df[['NumIdPersona', 'Segmento_poblacional']], on='NumIdPersona', how='left')

# 'Segmento_poblacional' y 'Producto' para contar la frecuencia de consumo
productos_por_segmento = consumo_con_segmento.groupby(['Segmento_poblacional', 'Producto']).size().reset_index(name='Frecuencia')

# frecuencia total de productos consumidos por cada segmento
frecuencia_total_por_segmento = productos_por_segmento.groupby('Segmento_poblacional')['Frecuencia'].sum().reset_index(name='Frecuencia_Total')

# frecuencia total con el DataFrame original
productos_por_segmento = pd.merge(productos_por_segmento, frecuencia_total_por_segmento, on='Segmento_poblacional')

# porcentaje de frecuencia de cada producto respecto al total
productos_por_segmento['Porcentaje'] = (productos_por_segmento['Frecuencia'] / productos_por_segmento['Frecuencia_Total']) * 100

#Ordenar por segmento y frecuencia (de mayor a menor)
productos_por_segmento_sorted = productos_por_segmento.sort_values(by=['Segmento_poblacional', 'Frecuencia'], ascending=[True, False])

#2 productos más consumidos por cada segmento poblacional
productos_top2_por_segmento = productos_por_segmento_sorted.groupby('Segmento_poblacional').head(2)

#Redondear los porcentajes a 2 decimales
productos_top2_por_segmento['Porcentaje'] = productos_top2_por_segmento['Porcentaje'].round(2)

# Mostrar los resultados
print("Los dos productos más consumidos por cada segmento poblacional con su frecuencia en porcentaje:")
print(tabulate(productos_top2_por_segmento[['Segmento_poblacional', 'Producto', 'Porcentaje']], 
               headers='keys', tablefmt='pretty', showindex=False))

print ("¿Cuáles son los productos más consumidos en el cada segmento poblacional?")

# Unir datos de consumo con el segmento poblacional
consumo_con_segmento = pd.merge(consumo_df, persona_df[['NumIdPersona', 'Segmento_poblacional']], on='NumIdPersona', how='left')

# valores en blanco'Segmento_poblacional' (SIN inplace=True)
consumo_con_segmento['Segmento_poblacional'] = consumo_con_segmento['Segmento_poblacional'].fillna('Desconocido')

#  'Segmento_poblacional' y 'Producto' para contar la frecuencia de consumo
productos_por_segmento = consumo_con_segmento.groupby(['Segmento_poblacional', 'Producto']).size().reset_index(name='Frecuencia')

# frecuencia total por segmento
frecuencia_total_por_segmento = productos_por_segmento.groupby('Segmento_poblacional')['Frecuencia'].sum().reset_index(name='Frecuencia_Total')

# frecuencia total
productos_por_segmento = pd.merge(productos_por_segmento, frecuencia_total_por_segmento, on='Segmento_poblacional')

# Calcular porcentaje
productos_por_segmento['Porcentaje'] = (productos_por_segmento['Frecuencia'] / productos_por_segmento['Frecuencia_Total']) * 100

# Ordenar datos por segmento y frecuencia descendente
productos_por_segmento_sorted = productos_por_segmento.sort_values(by=['Segmento_poblacional', 'Frecuencia'], ascending=[True, False])

# 2 productos más consumidos por cada segmento y hacer una copia explícita
productos_top2_por_segmento = productos_por_segmento_sorted.groupby('Segmento_poblacional').head(2).copy()

# Redondear porcentaje a 2 decimales
productos_top2_por_segmento['Porcentaje'] = productos_top2_por_segmento['Porcentaje'].round(2)

# Mostrar resultados
print("\nLos dos productos más consumidos por cada segmento poblacional con su frecuencia en porcentaje:\n")
print(tabulate(productos_top2_por_segmento[['Segmento_poblacional', 'Producto', 'Porcentaje']], 
               headers='keys', tablefmt='pretty', showindex=False))


print("¿Cuáles son las mejores empresas en cuanto a consumo individual de sus empleados?")

# Unir consumo con personas para obtener el id_empresa de cada empleado
consumo_persona_empresa = pd.merge(consumo_df, persona_df[['NumIdPersona', 'id_empresa']], on='NumIdPersona', how='left')

# Calcular el consumo total por persona
consumo_por_persona = consumo_persona_empresa.groupby('NumIdPersona')['Valor'].sum().reset_index(name='Consumo_Total')

# valor de  empresa a cada consumo individual
consumo_por_persona = pd.merge(consumo_por_persona, persona_df[['NumIdPersona', 'id_empresa']], on='NumIdPersona', how='left')

# Se calcula el promedio de consumo 
consumo_por_empresa = consumo_por_persona.groupby('id_empresa')['Consumo_Total'].mean().reset_index(name='Consumo_Promedio_Empleado')

# Unir con los nombres de las empresas (columna correcta: 'Piramide2')
consumo_por_empresa = pd.merge(consumo_por_empresa, empresa_df[['id_empresa', 'Piramide2']], on='id_empresa', how='left')

#empresas de mayor a menor consumo promedio por empleado
empresas_top_consumo = consumo_por_empresa.sort_values(by='Consumo_Promedio_Empleado', ascending=False)

# consumo promedio como moneda
empresas_top_consumo['Consumo_Promedio_Empleado'] = empresas_top_consumo['Consumo_Promedio_Empleado'].apply(lambda x: "${:,.2f}".format(x))

# Mostrar los resultados
print("\n Las Mejores empresas segun consumo promedio individual de sus empleados 🏆\n")
print(tabulate(empresas_top_consumo[['id_empresa', 'Piramide2', 'Consumo_Promedio_Empleado']], 
               headers=['ID Empresa', 'Empresa', 'Consumo Promedio por Empleado'], tablefmt='pretty', showindex=False))



# Voy a pasar todos los resultados de cada punto a un json
resultados = {
    "temporadas_venta": ventas_maximas_por_periodo.to_dict(orient='records'),
    "consumo_por_ues": consumo_total_por_ues.to_dict(orient='records'),
    "participacion_consumo": {
        "afiliadas": f"{porcentaje_afiliadas:.2f}%",
        "no_afiliadas": f"{porcentaje_no_afiliadas:.2f}%"
    },
    "productos_mas_usados": producto_mas_usado_por_ues[['UES', 'Producto', '% Mayor-Uso']].to_dict(orient='records'),
    "clientes_mayor_frecuencia": clientes_mayor_frecuencia.to_dict(orient='records'),
    "clientes_mayor_valor": clientes_mayor_valor.to_dict(orient='records'),
    "penetracion_afiliados": afiliados_por_periodo[['Periodo', 'Clientes_Con_Consumo', 'Porcentaje_Penetracion']].to_dict(orient='records'),
    "penetracion_no_afiliados": no_afiliados_por_periodo[['Periodo', 'Clientes_Con_Consumo', 'Porcentaje_Penetracion']].to_dict(orient='records'),
    "productos_segmento": productos_top2_por_segmento[['Segmento_poblacional', 'Producto', 'Porcentaje']].to_dict(orient='records'),
    "mejores_empresas": empresas_top_consumo[['id_empresa', 'Piramide2', 'Consumo_Promedio_Empleado']].to_dict(orient='records')
}

with open('Web/resultados.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print("el archivo se a generado correctamente, los resultados.")