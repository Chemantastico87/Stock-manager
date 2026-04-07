import flet as ft
import json
import os
from datetime import datetime

class StockApp:
    def __init__(self):
        self.data_file = "stock_productos.json"
        self.productos = self.cargar_datos()
        self.page = None
        
    def cargar_datos(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except:
                return []
        return []
    
    def guardar_datos(self):
        with open(self.data_file, 'w', encoding='utf-8') as file:
            json.dump(self.productos, file, indent=4, ensure_ascii=False)
    
    def mostrar_snackbar(self, mensaje, es_error=False):
        color = "#F44336" if es_error else "#4CAF50"
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            bgcolor=color,
            action="OK"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Control de Stock"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 10
        page.scroll = ft.ScrollMode.AUTO
        page.bgcolor = "#F5F5F5"
        
        nombre_field = ft.TextField(
            label="Nombre del producto",
            hint_text="Ej: Hamburguesa, Papas...",
            width=page.width - 20,
            prefix_icon=ft.icons.FASTFOOD,
            border_color="#2196F3"
        )
        
        cantidad_field = ft.TextField(
            label="Cantidad (kg)",
            hint_text="Ej: 5.5",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=page.width - 20,
            prefix_icon=ft.icons.SCALE,
            border_color="#2196F3"
        )
        
        busqueda_field = ft.TextField(
            label="Buscar producto",
            prefix_icon=ft.icons.SEARCH,
            width=page.width - 20,
            border_color="#2196F3",
            on_change=lambda e: cargar_lista(e.control.value)
        )
        
        lista_productos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        total_productos_text = ft.Text("0", size=14, weight=ft.FontWeight.BOLD, color="#2196F3")
        total_kgs_text = ft.Text("0 kg", size=14, weight=ft.FontWeight.BOLD, color="#4CAF50")
        
        resumen_container = ft.Container(
            content=ft.Column([
                ft.Text("📊 Resumen", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([ft.Icon(ft.icons.INVENTORY, color="#2196F3"), ft.Text("Productos:", size=14), total_productos_text]),
                ft.Row([ft.Icon(ft.icons.SCALE, color="#4CAF50"), ft.Text("Total kg:", size=14), total_kgs_text]),
            ]),
            padding=15,
            bgcolor="white",
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        )
        
        alertas_lista = ft.Column(spacing=5)
        alertas_container = ft.Container(
            visible=False,
            padding=10,
            bgcolor="#FFEBEE",
            border_radius=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.WARNING, color="#F44336"), ft.Text("⚠️ STOCK BAJO", size=14, weight=ft.FontWeight.BOLD, color="#F44336")]),
                alertas_lista
            ])
        )
        
        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("➕ Agregar Producto", size=18, weight=ft.FontWeight.BOLD),
                    nombre_field,
                    cantidad_field,
                    ft.ElevatedButton("Agregar", icon=ft.icons.ADD, bgcolor="#4CAF50", color="white", on_click=lambda e: agregar_producto()),
                ]),
                padding=20
            )
        )
        
        def actualizar_resumen():
            total_productos = len(self.productos)
            total_kgs = sum(p["cantidad"] for p in self.productos)
            total_productos_text.value = str(total_productos)
            total_kgs_text.value = f"{total_kgs:.1f} kg"
            
            productos_stock_bajo = [p for p in self.productos if p["cantidad"] < 10]
            if productos_stock_bajo:
                alertas_container.visible = True
                alertas_lista.controls.clear()
                for p in productos_stock_bajo:
                    alertas_lista.controls.append(ft.Container(content=ft.Text(f"• {p['nombre']}: {p['cantidad']:.1f} kg", color="#F44336"), padding=5))
            else:
                alertas_container.visible = False
            page.update()
        
        def actualizar_cantidad(producto, cambio):
            nueva_cantidad = producto["cantidad"] + cambio
            if nueva_cantidad < 0:
                self.mostrar_snackbar("No puede tener stock negativo", True)
                return
            producto["cantidad"] = nueva_cantidad
            self.guardar_datos()
            cargar_lista(busqueda_field.value)
        
        def eliminar_producto(producto):
            def confirmar(e):
                self.productos = [p for p in self.productos if p["id"] != producto["id"]]
                self.guardar_datos()
                cargar_lista(busqueda_field.value)
                dialog.open = False
                page.update()
                self.mostrar_snackbar(f"✅ '{producto['nombre']}' eliminado")
            
            def cancelar(e):
                dialog.open = False
                page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar"),
                content=ft.Text(f"¿Eliminar '{producto['nombre']}'?"),
                actions=[ft.TextButton("Cancelar", on_click=cancelar), ft.ElevatedButton("Eliminar", on_click=confirmar, bgcolor="#F44336", color="white")]
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def cargar_lista(filtro=""):
            lista_productos.controls.clear()
            productos_filtrados = [p for p in self.productos if filtro.lower() in p["nombre"].lower()] if filtro else self.productos
            
            if not productos_filtrados:
                lista_productos.controls.append(ft.Container(content=ft.Text("📭 No hay productos", italic=True, color="#9E9E9E"), padding=20, alignment=ft.alignment.center))
            else:
                for p in productos_filtrados:
                    tarjeta = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.FASTFOOD, color="#2196F3"),
                                    ft.Text(p["nombre"], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                    ft.IconButton(icon=ft.icons.DELETE, icon_color="#F44336", icon_size=20, on_click=lambda e, prod=p: eliminar_producto(prod))
                                ]),
                                ft.Divider(),
                                ft.Row([
                                    ft.Icon(ft.icons.SCALE, color="#4CAF50", size=30),
                                    ft.Column([ft.Text("Cantidad:", size=12, color="#757575"), ft.Text(f"{p['cantidad']:.1f} kg", size=24, weight=ft.FontWeight.BOLD, color="#2196F3")], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([
                                    ft.ElevatedButton("-1 kg", icon=ft.icons.REMOVE, bgcolor="#F44336", color="white", expand=True, on_click=lambda e, prod=p: actualizar_cantidad(prod, -1)),
                                    ft.ElevatedButton("-0.5 kg", icon=ft.icons.REMOVE, bgcolor="#FF9800", color="white", expand=True, on_click=lambda e, prod=p: actualizar_cantidad(prod, -0.5)),
                                    ft.ElevatedButton("+1 kg", icon=ft.icons.ADD, bgcolor="#4CAF50", color="white", expand=True, on_click=lambda e, prod=p: actualizar_cantidad(prod, 1)),
                                ], spacing=5),
                                ft.Container(content=ft.Text("⚠️ STOCK BAJO" if p["cantidad"] < 10 else "✓ STOCK OK", color="white" if p["cantidad"] < 10 else "#4CAF50", size=12, weight=ft.FontWeight.BOLD), bgcolor="#F44336" if p["cantidad"] < 10 else "#E8F5E9", padding=8, border_radius=5, visible=p["cantidad"] < 10, alignment=ft.alignment.center)
                            ]),
                            padding=15,
                            bgcolor="#FFEBEE" if p["cantidad"] < 10 else "white"
                        )
                    )
                    lista_productos.controls.append(tarjeta)
            actualizar_resumen()
            page.update()
        
        def agregar_producto():
            nombre = nombre_field.value.strip() if nombre_field.value else ""
            cantidad = cantidad_field.value.strip() if cantidad_field.value else ""
            if not nombre or not cantidad:
                self.mostrar_snackbar("Complete todos los campos", True)
                return
            try:
                cantidad = float(cantidad)
                if cantidad <= 0:
                    raise ValueError()
                if any(p["nombre"].lower() == nombre.lower() for p in self.productos):
                    self.mostrar_snackbar("Ya existe ese producto", True)
                    return
                nuevo_id = max([p["id"] for p in self.productos], default=0) + 1
                self.productos.append({"id": nuevo_id, "nombre": nombre, "cantidad": cantidad, "fecha": datetime.now().strftime("%Y-%m-%d")})
                self.guardar_datos()
                cargar_lista(busqueda_field.value)
                nombre_field.value = ""
                cantidad_field.value = ""
                self.mostrar_snackbar(f"✅ '{nombre}' agregado")
            except:
                self.mostrar_snackbar("Cantidad inválida", True)
        
        if not self.productos:
            self.productos = [
                {"id": 1, "nombre": "Hamburguesa", "cantidad": 25, "fecha": datetime.now().strftime("%Y-%m-%d")},
                {"id": 2, "nombre": "Pan", "cantidad": 50, "fecha": datetime.now().strftime("%Y-%m-%d")},
                {"id": 3, "nombre": "Queso", "cantidad": 8, "fecha": datetime.now().strftime("%Y-%m-%d")},
                {"id": 4, "nombre": "Papas", "cantidad": 30, "fecha": datetime.now().strftime("%Y-%m-%d")},
            ]
            self.guardar_datos()
        
        page.add(ft.Container(content=ft.Column([
            ft.Text("🍔 Control de Stock", size=24, weight=ft.FontWeight.BOLD, color="#2196F3"),
            ft.Divider(),
            busqueda_field,
            resumen_container,
            alertas_container,
            form_card,
            ft.Text("📋 Productos", size=18, weight=ft.FontWeight.BOLD),
            lista_productos,
        ], scroll=ft.ScrollMode.AUTO), expand=True))
        
        cargar_lista("")

def main():
    ft.app(target=StockApp().main)

if __name__ == "__main__":
    main()
