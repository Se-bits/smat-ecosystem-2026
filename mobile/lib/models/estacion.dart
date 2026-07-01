class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;
  final double lectura; // <- Nuevo campo para el reto

  Estacion(
      {required this.id,
      required this.nombre,
      required this.ubicacion,
      required this.lectura});

  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'],
      nombre: json['nombre'],
      ubicacion: json['ubicacion'],
      // Si el servidor aún no envía 'lectura', puedes poner un valor por defecto (ej. 40.0)
      // para que la app no se rompa mientras el profesor actualiza el backend.
      lectura: json['lectura'] ?? 0.0,
    );
  }
}
