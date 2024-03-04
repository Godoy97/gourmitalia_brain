import streamlit as st
import pandas as pd
import altair as alt
import calendar

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # Convert 'Fecha Documento' column to datetime format
    df['Fecha Documento'] = pd.to_datetime(df['Fecha Documento'], format='%d/%m/%Y')
    # df = df.dropna(subset=['Sucursal'])
    # df.loc[(df['Cliente'] == 'Sin cliente') & (df['Tracking Number'].notna()), 'Sucursal'] = 'Shopify'

    return df


def main():
    df = load_data()
    st.title('Sales Dashboard: Último año de ventas')

    # Add date picker filter

    branches = st.multiselect(
        "Seleccione una Sucursal", df['Sucursal'].unique(), ["CASA MATRIZ"]
    )

    products = st.multiselect(
        "Seleccione un Producto or Servicio", df['Producto / Servicio'].unique(),
    )

    customers = st.multiselect(
    "Seleccione un Cliente (Opcional)", df['Cliente'].unique(),
    )

    if not branches:
        st.error("Por favor seleccione almenos una Sucursal.")
        st.stop()

     # Initialize the markdown string
    markdown_string = ""

    st.write("### Ventas para los filtros aplicados:")

    # Create a new DataFrame to hold sales data for all branches
    all_branches_monthly_sales = pd.DataFrame()

    for branch in branches:
        # Calculate total sales
        filtered_df = df[df['Sucursal'] == branch]
        total_branch = filtered_df['Subtotal Bruto'].sum()
        markdown_string += f"* **Ventas Totales {branch}:** ${total_branch:,.0f}\n"

        # Calculate total sales per month for the branch
        filtered_df = df[df['Sucursal'] == branch]
        monthly_sales = filtered_df.resample('M', on='Fecha Documento')['Subtotal Bruto'].sum()
        monthly_sales.name = branch  # Name the series after the branch
        monthly_sales.index = monthly_sales.index.strftime('%Y-%m')
        all_branches_monthly_sales = pd.concat([all_branches_monthly_sales, monthly_sales], axis=1).sort_index()


        for product in products:
            filtered_df = df[
                (df['Sucursal'] == branch) &
                (df['Producto / Servicio'] == product)
            ]
            total_product = filtered_df['Subtotal Bruto'].sum()
            markdown_string += f"    * **Ventas Totales {product} en {branch}:** ${total_product:,.0f}\n"
            for customer in customers:
                filtered_df = df[
                    (df['Sucursal'] == branch) &
                    (df['Producto / Servicio'] == product) &
                    (df['Cliente'] == customer)
                ]
                total_customer = filtered_df['Subtotal Bruto'].sum()
                markdown_string += f"        * **Ventas Totales {customer} en {product} en {branch}:** ${total_customer:,.0f}\n"

    # Display the markdown string
    st.markdown(markdown_string)
    # Charts by branch
    st.write("### Ventas Totales por Mes para todas las Sucursales seleccionadas:")
    st.bar_chart(all_branches_monthly_sales)

    # Filter the data
    filtered_df = df[
    (df['Sucursal'].isin(branches)) &
    (df['Cliente'].isin(customers) if customers else True) &
    (df['Producto / Servicio'].isin(products) if products else True)
    ]
    # st.write(f"Ventas Totales por Sucursal: {total_branch}")

    #Show data about the p

    # Visualize sales trends over time
    # Charts
    if not filtered_df.empty and products:
        st.write("### Gráficas:")
        chart_data = filtered_df.groupby(['Fecha Documento', 'Producto / Servicio'])['Subtotal Bruto'].sum().reset_index()

        chart = (
            alt.Chart(chart_data)
            .mark_line(point=True)  # Connect the dots with lines
            .encode(
                x=alt.X('Fecha Documento:T', title='Fecha Documento'), # %B for full month name
                y=alt.Y('Subtotal Bruto:Q', title='Subtotal Bruto'), # No need to format here
                color='Producto / Servicio:N',
                # tooltip=['Fecha Documento:T', '(Subtotal Bruto):Q']
            )
            .properties(
                width=700,
                height=400,
                title='Tendencias de Ventas en el Tiempo filtros aplicados',
            )
        )

        st.altair_chart(chart, use_container_width=True)

        # new way
        # First, ensure your DataFrame includes 'Sucursal' in the groupby operation.
        chart_data = filtered_df.groupby(['Fecha Documento', 'Sucursal', 'Producto / Servicio'])['Subtotal Bruto'].sum().reset_index()

        # Add a new column to 'chart_data' that concatenates 'Sucursal' and 'Producto / Servicio'
        chart_data['Branch_Product'] = chart_data['Sucursal'] + ' - ' + chart_data['Producto / Servicio']

        # Update your Altair chart to use 'Branch_Product' for color encoding
        chart = (
            alt.Chart(chart_data)
            .mark_line(point=True)  # Use line marks for the chart
            .encode(
                x=alt.X('Fecha Documento:T', title='Fecha Documento'),
                y=alt.Y('Subtotal Bruto:Q', title='Subtotal Bruto'),
                color=alt.Color('Branch_Product:N', legend=alt.Legend(title="Sucursal y Producto/Servicio")),  # Now using 'Branch_Product' for color
                tooltip=['Fecha Documento:T', 'Sucursal:N', 'Producto / Servicio:N', 'Subtotal Bruto:Q']
            )
            .properties(
                width=700,
                height=400,
                title='Tendencias de Ventas en el Tiempo por Sucursal y Producto/Servicio',
            )
        )

        st.altair_chart(chart, use_container_width=True)
        # st.write(chart_data)
    st.write("### Data de ventas para los filtros aplicados:")
    st.write(filtered_df)
    st.download_button('Descargar CSV', filtered_df.to_csv(), 'sales_data.csv', 'text/csv')






    # #Using object notation
    # add_selectbox = st.sidebar.selectbox(
    # "How would you like to be contacted?",
    # ("Email", "Home phone", "Mobile phone")
    # )
    # st.write(add_selectbox)


if __name__ == '__main__':
    main()

#Filtro de tiempo
# CHECK Si no hay producto seleccionado mostrar grafica de ventas mensuales por sucursal CHECK
# Grafico seperado por sucursal en el que tiene todos los filtros
