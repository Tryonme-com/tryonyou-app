# TRYONYOU: ZERO-SIZE PROTOCOL & PRIVACY FIREWALL

## 1. La Directiva "Zero-Size" (Cero Complejos)
El ecosistema TryOnYou rechaza el sistema de tallaje tradicional (S, M, L) por considerarlo obsoleto. Según la Primera Directiva de las "Backend Golden Rules": Bajo ninguna circunstancia la API devolverá una etiqueta de talla cruda (ej. 'XL', '42', 'Talla 10') al frontend para ser expuesta al usuario.

## 2. Privacy Firewall y Lógica de Elasticidad
El sistema ejecuta un `PrivacyFirewall` que aplica reglas de expresiones regulares (Regex) para interceptar, bloquear y destruir cualquier talla o medida exacta (como kg, cm, S, M, L) antes de que la información alcance la interfaz visual.

## 3. Fit Score y Motor Físico (Agente 70)
Las medidas numéricas espaciales extraídas de los landmarks biométricos (como la anchura de hombros) no buscan encajar en una matriz de tallas estándar. En su lugar, el Motor Físico (Agente 70) cruza la deformación espacial geométrica del usuario con los perfiles reales de los tejidos:
- Coeficiente de caída (*drape*)
- Porcentaje de elasticidad
- Tensión del material

El objetivo algorítmico es calcular un "Fit Score" preciso para identificar la prenda única que posee la caída arquitectónica perfecta sobre esa silueta específica.

## 4. Live AR y "Certeza Absoluta"
La capa de frontend de Live AR ancla la prenda digital, aplicando escalado dinámico (`garmentWidth`, `garmentHeight`) para seguir el movimiento corporal en vivo de forma impecable. La omisión estructural de las tallas tradicionales tiene el propósito inquebrantable de entregar al usuario una "Certeza Absoluta" (un doble digital con la ropa perfecta), eliminando la ansiedad del retail y devolviendo la dignidad a la experiencia de usuario.
