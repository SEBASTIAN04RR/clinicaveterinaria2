import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class ClinicaVeterinaria:
    def __init__(self):
        self.conn = sqlite3.connect('clinica_veterinaria.db')
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nombre TEXT,
                                especie TEXT,
                                raza TEXT,
                                edad INTEGER,
                                propietario TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_paciente INTEGER,
                                fecha TEXT,
                                hora TEXT,
                                motivo TEXT,
                                FOREIGN KEY (id_paciente) REFERENCES pacientes (id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nombre TEXT UNIQUE,
                                cantidad INTEGER,
                                precio REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nombre TEXT,
                                cantidad INTEGER,
                                precio REAL)''')
        self.conn.commit()

    def registrar_paciente(self, paciente):
        self.cursor.execute("INSERT INTO pacientes (nombre, especie, raza, edad, propietario) VALUES (?, ?, ?, ?, ?)",
                            (paciente['nombre'], paciente['especie'], paciente['raza'], paciente['edad'], paciente['propietario']))
        self.conn.commit()

    def obtener_pacientes(self):
        self.cursor.execute("SELECT * FROM pacientes")
        return self.cursor.fetchall()

    def actualizar_paciente(self, paciente):
        self.cursor.execute("UPDATE pacientes SET nombre = ?, especie = ?, raza = ?, edad = ?, propietario = ? WHERE id = ?",
                            (paciente['nombre'], paciente['especie'], paciente['raza'], paciente['edad'], paciente['propietario'], paciente['id']))
        self.conn.commit()

    def programar_cita(self, cita):
        self.cursor.execute("INSERT INTO citas (id_paciente, fecha, hora, motivo) VALUES (?, ?, ?, ?)",
                            (cita['id_paciente'], cita['fecha'], cita['hora'], cita['motivo']))
        self.conn.commit()

    def obtener_citas(self):
        self.cursor.execute("SELECT citas.id, pacientes.nombre, citas.fecha, citas.hora, citas.motivo FROM citas JOIN pacientes ON citas.id_paciente = pacientes.id")
        return self.cursor.fetchall()

    def registrar_medicamento(self, medicamento):
        self.cursor.execute("INSERT OR IGNORE INTO medicamentos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                            (medicamento['nombre'], medicamento['cantidad'], medicamento['precio']))
        self.cursor.execute("UPDATE medicamentos SET cantidad = cantidad + ?, precio = ? WHERE nombre = ?",
                            (medicamento['cantidad'], medicamento['precio'], medicamento['nombre']))
        self.conn.commit()

    def actualizar_medicamento(self, nombre, cantidad, precio):
        self.cursor.execute("UPDATE medicamentos SET cantidad = ?, precio = ? WHERE nombre = ?",
                            (cantidad, precio, nombre))
        self.conn.commit()

    def vender_medicamento(self, nombre_medicamento, cantidad_vendida):
        self.cursor.execute("SELECT cantidad, precio FROM medicamentos WHERE nombre = ?", (nombre_medicamento,))
        resultado = self.cursor.fetchone()
        if resultado:
            cantidad_actual, precio = resultado
            if cantidad_actual >= cantidad_vendida:
                nueva_cantidad = cantidad_actual - cantidad_vendida
                self.cursor.execute("UPDATE medicamentos SET cantidad = ? WHERE nombre = ?",
                                    (nueva_cantidad, nombre_medicamento))
                self.cursor.execute("INSERT INTO ventas (nombre, cantidad, precio) VALUES (?, ?, ?)",
                                    (nombre_medicamento, cantidad_vendida, precio * cantidad_vendida))
                self.conn.commit()
                return True
            else:
                return False
        return None

    def obtener_medicamentos(self):
        self.cursor.execute("SELECT nombre, cantidad, precio FROM medicamentos")
        return self.cursor.fetchall()

    def obtener_ventas(self):
        self.cursor.execute("SELECT nombre, cantidad, precio FROM ventas")
        return self.cursor.fetchall()

    def alerta_inventario_bajo(self):
        alertas = []
        self.cursor.execute("SELECT nombre FROM medicamentos WHERE cantidad <= 10")
        medicamentos = self.cursor.fetchall()
        for medicamento in medicamentos:
            alertas.append(f"El medicamento {medicamento[0]} tiene un inventario bajo.")
        return alertas

    def verificar_usuario(self, usuario, contrasena):
        return usuario == "Clinica Cute Pets" and contrasena == "Lucas18yaeslegal"

class LoginWindow:
    def __init__(self, root, clinica):
        self.root = root
        self.clinica = clinica
        self.root.title("Clínica Veterinaria Cute Pets")
        self.root.geometry("400x300")
        self.estilo_widgets()
        self.tab_control = ttk.Notebook(root)
        self.tab_login = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_login, text="Login Empleados")
        self.tab_control.pack(expand=1, fill="both")
        self.crear_tab_login()

    def estilo_widgets(self):
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#5F9EA0", foreground="black", font=("Helvetica", 10, "bold"))
        style.configure("TLabel", background="#F0F8FF", foreground="#2F4F4F", font=("Helvetica", 10, "bold"))
        style.configure("TEntry", fieldbackground="#FAFAD2", foreground="black", font=("Helvetica", 10, "bold"))
        self.root.configure(background="#F5DEB3")

    def crear_tab_login(self):
        frame = ttk.Frame(self.tab_login)
        frame.pack(expand=1, fill="both")
        
        ttk.Label(frame, text="Usuario").grid(row=0, column=0, pady=5, padx=5)
        self.usuario_entry = ttk.Entry(frame)
        self.usuario_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Contraseña").grid(row=1, column=0, pady=5, padx=5)
        self.contrasena_entry = ttk.Entry(frame, show="*")
        self.contrasena_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Ingresar", command=self.verificar_login).grid(row=2, columnspan=2, pady=10, padx=5)

    def verificar_login(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contrasena_entry.get()
        if self.clinica.verificar_usuario(usuario, contrasena):
            self.tab_control.forget(self.tab_login)
            self.crear_tabs()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def crear_tabs(self):
        self.tab_pacientes = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_pacientes, text="Pacientes")
        PacientesTab(self.tab_pacientes, self.clinica)

        self.tab_citas = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_citas, text="Citas")
        CitasTab(self.tab_citas, self.clinica)

        self.tab_reportes = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_reportes, text="Reportes")
        ReportesTab(self.tab_reportes, self.clinica)

        self.tab_registro_medicamentos = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_registro_medicamentos, text="Registro de Medicamentos y Suministros")
        RegistroMedicamentosTab(self.tab_registro_medicamentos, self.clinica)

        self.tab_inventario = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_inventario, text="Inventario")
        InventarioTab(self.tab_inventario, self.clinica)

        self.tab_venta_medicamentos = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_venta_medicamentos, text="Venta de Medicamentos")
        VentaMedicamentosTab(self.tab_venta_medicamentos, self.clinica)

        self.tab_medicamentos_vendidos = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_medicamentos_vendidos, text="Medicamentos Vendidos")
        MedicamentosVendidosTab(self.tab_medicamentos_vendidos, self.clinica)

        self.tab_pacientes_registrados = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_pacientes_registrados, text="Pacientes Registrados")
        PacientesRegistradosTab(self.tab_pacientes_registrados, self.clinica)

class PacientesTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_pacientes()

    def crear_tab_pacientes(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")
        
        ttk.Label(frame, text="Nombre").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_entry = ttk.Entry(frame)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Especie").grid(row=1, column=0, pady=5, padx=5)
        self.especie_entry = ttk.Entry(frame)
        self.especie_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Raza").grid(row=2, column=0, pady=5, padx=5)
        self.raza_entry = ttk.Entry(frame)
        self.raza_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Edad").grid(row=3, column=0, pady=5, padx=5)
        self.edad_entry = ttk.Entry(frame)
        self.edad_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Propietario").grid(row=4, column=0, pady=5, padx=5)
        self.propietario_entry = ttk.Entry(frame)
        self.propietario_entry.grid(row=4, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Registrar", command=self.registrar_paciente).grid(row=5, columnspan=2, pady=10, padx=5)

    def registrar_paciente(self):
        paciente = {
            'nombre': self.nombre_entry.get(),
            'especie': self.especie_entry.get(),
            'raza': self.raza_entry.get(),
            'edad': int(self.edad_entry.get()),
            'propietario': self.propietario_entry.get()
        }
        self.clinica.registrar_paciente(paciente)
        messagebox.showinfo("Éxito", "Paciente registrado correctamente")

class CitasTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_citas()

    def crear_tab_citas(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")
        
        ttk.Label(frame, text="Paciente").grid(row=0, column=0, pady=5, padx=5)
        self.paciente_combobox = ttk.Combobox(frame)
        self.paciente_combobox.grid(row=0, column=1, pady=5, padx=5)
        self.actualizar_pacientes()

        ttk.Label(frame, text="Fecha").grid(row=1, column=0, pady=5, padx=5)
        self.fecha_entry = ttk.Entry(frame)
        self.fecha_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Hora").grid(row=2, column=0, pady=5, padx=5)
        self.hora_entry = ttk.Entry(frame)
        self.hora_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Motivo").grid(row=3, column=0, pady=5, padx=5)
        self.motivo_entry = ttk.Entry(frame)
        self.motivo_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Programar Cita", command=self.programar_cita).grid(row=4, columnspan=2, pady=10, padx=5)

    def actualizar_pacientes(self):
        pacientes = self.clinica.obtener_pacientes()
        self.paciente_combobox['values'] = [paciente[1] for paciente in pacientes]

    def programar_cita(self):
        paciente_nombre = self.paciente_combobox.get()
        self.clinica.cursor.execute("SELECT id FROM pacientes WHERE nombre = ?", (paciente_nombre,))
        id_paciente = self.clinica.cursor.fetchone()[0]
        fecha = self.fecha_entry.get()
        hora = self.hora_entry.get()
        motivo = self.motivo_entry.get()
        cita = {'id_paciente': id_paciente, 'fecha': fecha, 'hora': hora, 'motivo': motivo}
        self.clinica.programar_cita(cita)
        messagebox.showinfo("Éxito", "Cita programada correctamente")

class ReportesTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_reportes()

    def crear_tab_reportes(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")

        self.tree = ttk.Treeview(frame, columns=("ID", "Paciente", "Fecha", "Hora", "Motivo"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Paciente", text="Paciente")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Motivo", text="Motivo")
        self.tree.pack(expand=1, fill="both")

        ttk.Button(frame, text="Generar Reporte de Citas", command=self.generar_reporte_citas).pack(pady=10)

    def generar_reporte_citas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        citas = self.clinica.obtener_citas()
        for cita in citas:
            self.tree.insert("", "end", values=cita)

class RegistroMedicamentosTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_registro_medicamentos()

    def crear_tab_registro_medicamentos(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")
        
        ttk.Label(frame, text="Nombre del Medicamento").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_entry = ttk.Entry(frame)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Cantidad").grid(row=1, column=0, pady=5, padx=5)
        self.cantidad_entry = ttk.Entry(frame)
        self.cantidad_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Precio").grid(row=2, column=0, pady=5, padx=5)
        self.precio_entry = ttk.Entry(frame)
        self.precio_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Registrar", command=self.registrar_medicamento).grid(row=3, columnspan=2, pady=10, padx=5)

    def registrar_medicamento(self):
        nombre = self.nombre_entry.get()
        cantidad = int(self.cantidad_entry.get())
        precio = float(self.precio_entry.get())
        medicamento = {'nombre': nombre, 'cantidad': cantidad, 'precio': precio}
        self.clinica.registrar_medicamento(medicamento)
        messagebox.showinfo("Éxito", "Medicamento registrado correctamente")

class InventarioTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_inventario()

    def crear_tab_inventario(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")

        self.tree = ttk.Treeview(frame, columns=("Nombre", "Cantidad", "Precio"), show='headings')
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio")
        self.tree.pack(expand=1, fill="both")

        ttk.Button(frame, text="Actualizar Inventario", command=self.actualizar_inventario).pack(pady=10)

        self.actualizar_inventario()

    def actualizar_inventario(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        medicamentos = self.clinica.obtener_medicamentos()
        for medicamento in medicamentos:
            self.tree.insert("", "end", values=medicamento)
        alertas = self.clinica.alerta_inventario_bajo()
        if alertas:
            messagebox.showwarning("Alerta de Inventario Bajo", "\n".join(alertas))

class VentaMedicamentosTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_venta_medicamentos()

    def crear_tab_venta_medicamentos(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")

        ttk.Label(frame, text="Nombre del Medicamento").grid(row=0, column=0, pady=5, padx=5)
        self.nombre_entry = ttk.Entry(frame)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Cantidad").grid(row=1, column=0, pady=5, padx=5)
        self.cantidad_entry = ttk.Entry(frame)
        self.cantidad_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Vender", command=self.vender_medicamento).grid(row=2, columnspan=2, pady=10, padx=5)

    def vender_medicamento(self):
        nombre_medicamento = self.nombre_entry.get()
        cantidad_vendida = int(self.cantidad_entry.get())
        resultado = self.clinica.vender_medicamento(nombre_medicamento, cantidad_vendida)
        if resultado is True:
            messagebox.showinfo("Éxito", "Medicamento vendido correctamente")
        elif resultado is False:
            messagebox.showerror("Error", "Cantidad insuficiente en el inventario")
        else:
            messagebox.showerror("Error", "Medicamento no encontrado")

class MedicamentosVendidosTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_medicamentos_vendidos()

    def crear_tab_medicamentos_vendidos(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")

        self.tree = ttk.Treeview(frame, columns=("Nombre", "Cantidad", "Precio"), show='headings')
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio")
        self.tree.pack(expand=1, fill="both")

        ttk.Button(frame, text="Actualizar Lista de Ventas", command=self.actualizar_lista_ventas).pack(pady=10)

        self.actualizar_lista_ventas()

    def actualizar_lista_ventas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        ventas = self.clinica.obtener_ventas()
        for venta in ventas:
            self.tree.insert("", "end", values=venta)

class PacientesRegistradosTab:
    def __init__(self, tab, clinica):
        self.tab = tab
        self.clinica = clinica
        self.crear_tab_pacientes_registrados()

    def crear_tab_pacientes_registrados(self):
        frame = ttk.Frame(self.tab)
        frame.pack(expand=1, fill="both")

        self.tree = ttk.Treeview(frame, columns=("ID", "Nombre", "Especie", "Raza", "Edad", "Propietario"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Especie", text="Especie")
        self.tree.heading("Raza", text="Raza")
        self.tree.heading("Edad", text="Edad")
        self.tree.heading("Propietario", text="Propietario")
        self.tree.pack(expand=1, fill="both")

        ttk.Button(frame, text="Actualizar Lista de Pacientes", command=self.actualizar_lista_pacientes).pack(pady=10)
        ttk.Button(frame, text="Editar Paciente", command=self.editar_paciente).pack(pady=10)

        self.actualizar_lista_pacientes()

    def actualizar_lista_pacientes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        pacientes = self.clinica.obtener_pacientes()
        for paciente in pacientes:
            self.tree.insert("", "end", values=paciente)

    def editar_paciente(self):
        item = self.tree.selection()
        if item:
            paciente_id = self.tree.item(item, 'values')[0]
            paciente = self.clinica.obtener_pacientes()
            for p in paciente:
                if p[0] == paciente_id:
                    self.editar_paciente_ventana(p)
                    break

    def editar_paciente_ventana(self, paciente):
        edit_window = tk.Toplevel(self.tab)
        edit_window.title("Editar Paciente")
        edit_window.geometry("400x300")

        ttk.Label(edit_window, text="Nombre").grid(row=0, column=0, pady=5, padx=5)
        nombre_entry = ttk.Entry(edit_window)
        nombre_entry.grid(row=0, column=1, pady=5, padx=5)
        nombre_entry.insert(0, paciente[1])

        ttk.Label(edit_window, text="Especie").grid(row=1, column=0, pady=5, padx=5)
        especie_entry = ttk.Entry(edit_window)
        especie_entry.grid(row=1, column=1, pady=5, padx=5)
        especie_entry.insert(0, paciente[2])

        ttk.Label(edit_window, text="Raza").grid(row=2, column=0, pady=5, padx=5)
        raza_entry = ttk.Entry(edit_window)
        raza_entry.grid(row=2, column=1, pady=5, padx=5)
        raza_entry.insert(0, paciente[3])

        ttk.Label(edit_window, text="Edad").grid(row=3, column=0, pady=5, padx=5)
        edad_entry = ttk.Entry(edit_window)
        edad_entry.grid(row=3, column=1, pady=5, padx=5)
        edad_entry.insert(0, paciente[4])

        ttk.Label(edit_window, text="Propietario").grid(row=4, column=0, pady=5, padx=5)
        propietario_entry = ttk.Entry(edit_window)
        propietario_entry.grid(row=4, column=1, pady=5, padx=5)
        propietario_entry.insert(0, paciente[5])

        def actualizar():
            datos_actualizados = {
                'id': paciente[0],
                'nombre': nombre_entry.get(),
                'especie': especie_entry.get(),
                'raza': raza_entry.get(),
                'edad': int(edad_entry.get()),
                'propietario': propietario_entry.get()
            }
            self.clinica.actualizar_paciente(datos_actualizados)
            messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
            self.actualizar_lista_pacientes()
            edit_window.destroy()

        ttk.Button(edit_window, text="Actualizar", command=actualizar).grid(row=5, columnspan=2, pady=10, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    clinica = ClinicaVeterinaria()
    app = LoginWindow(root, clinica)
    root.mainloop()
