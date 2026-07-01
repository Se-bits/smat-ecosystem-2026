import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/estacion.dart';
import 'login_screen.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;

  @override
  void initState() {
    super.initState();
    futureEstaciones = ApiService().fetchEstaciones();
  }

  void _refresh() {
    setState(() {
      futureEstaciones = ApiService().fetchEstaciones();
    });
  }

  void _mostrarDialogoEdicion(Estacion estacion) {
    final nombreCtrl = TextEditingController(text: estacion.nombre);
    final ubicacionCtrl = TextEditingController(text: estacion.ubicacion);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Editar Estación"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
                controller: nombreCtrl,
                decoration: const InputDecoration(labelText: "Nombre")),
            TextField(
                controller: ubicacionCtrl,
                decoration: const InputDecoration(labelText: "Ubicación")),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancelar")),
          ElevatedButton(
            onPressed: () async {
              // Llama a la función que acabamos de crear en api_service
              bool ok = await ApiService().editarEstacion(
                  estacion.id, nombreCtrl.text, ubicacionCtrl.text);
              if (ok) {
                if (!context.mounted) return;
                Navigator.pop(context);
                _refresh(); // Refresca la lista usando tu método existente
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Error al actualizar')),
                );
              }
            },
            child: const Text("Guardar"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await AuthService().logout(); // Limpia el token[cite: 1]
              // Reinicia la navegación al Login y borra el historial[cite: 1]
              if (!context.mounted) return;
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
          )
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return const Center(child: Text('❌ Error de conexión'));
          } else {
            // Validamos que existan datos antes de mostrar la lista
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return const Center(child: Text('No hay estaciones registradas'));
            }

            return RefreshIndicator(
              onRefresh: () async {
                setState(() {
                  futureEstaciones = ApiService().fetchEstaciones();
                });
              },
              child: ListView.builder(
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final est = snapshot.data![index];

                  return Dismissible(
                    key: Key(est.id.toString()),
                    direction: DismissDirection.endToStart,
                    background: Container(
                      color: Colors.red,
                      alignment: Alignment.centerRight,
                      padding: const EdgeInsets.only(right: 20),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    onDismissed: (direction) async {
                      bool ok = await ApiService().eliminarEstacion(est.id);
                      if (ok) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text("${est.nombre} eliminada")),
                        );
                      }
                    },
                    child: ListTile(
                      leading: Icon(
                        Icons.satellite_alt,
                        // Reto de colores. Se asume que est.lectura existe.
                        color: est.lectura > 50 ? Colors.red : Colors.green,
                      ),
                      title: Text(est.nombre),
                      subtitle: Text(est.ubicacion),
                      // ¡Activamos el toque para abrir el diálogo del Paso 3!
                      onTap: () => _mostrarDialogoEdicion(est),
                    ),
                  );
                },
              ),
            );
          } //no
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _refresh,
        child: const Icon(Icons.refresh),
      ),
    );
  }
}
