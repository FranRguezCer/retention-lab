# Reproducible February feature engineering
Objective: complete authorized Phase 3 only. Branch: feat/kkbox-feature-engineering.
Delivery: single final completion commit requested by user; no PR/merge. Runner: .venv-eda/bin/python -m unittest discover -s tests -v. Forecast: approximately 700 authored lines, one coherent processing unit, not artificial PR slices.

## Specs
- S1: “Quiero **implementar y completar la Fase 3 de Retention Lab**, trabajando en una rama nueva, y realizar **commit y push al remoto cuando todos los criterios de aceptación estén satisfechos**.” “No realices merge a `main` ni comiences la Fase 4.”
- S2: “Evita crear una segunda implementación independiente de elegibilidad, deduplicación, estados diarios o particionado.” Preserve original February RESTRICTED GO, cutoff 20170131, SHA-256 salt/buckets, 874580 labeled users and one exclusion; exact assignments and training EDA equivalence required.
- S3: “Mantén el número de variables pequeño y razonable.” Seven existing EDA signals; separate technical keys and outcomes; document provenance, conservative missing/ambiguity/date handling and train-only Phase 4 transformations.
- S4: “No leas, interpretes, exportes ni agregues etiquetas finales.” CSV transport necessarily parses fields but final values must never be evaluated, validated, hashed or exported. Validation labels only in a separate private artifact, no analytical use.
- S5: “Utiliza fixtures sintéticas pequeñas para pruebas de lógica y ejecuta las verificaciones pertinentes con los archivos reales disponibles localmente.” All twelve requested invariants: uniqueness, frozen population/splits, cutoff, predictor whitelist, disjointness, duplicates, daily ambiguity, invalid/missing, ordering, repeatability, final-label isolation and EDA compatibility.
- S6: “No consideres la fase terminada únicamente porque se hayan creado archivos.” Document schema/reproduction/results, verify real tables and prior EDA, private ignore/publication scan, then completion commit `feat(data): build reproducible cutoff-safe churn features`, push exact branch and verify remote SHA.

## Tasks
- T1 [S2,S3,S4] inline — VERIFIED — shared preparation and deterministic feature CLI. Risk: item 3 (shared EDA processing) and item 2 (outcome isolation); independent verifier required. No writer trigger.
- T2 [S5] inline synthetic suite 41 PASS; delegated independent scratch verification PASS; delegated long real preparation PASS (251.70 s), cache PASS (7.64 s), real EDA parity PASS (232.05 s).
- T3 [S1,S6] inline — acceptance/documentation/staged privacy VERIFIED; requested completion commit and remote confirmation recorded in delivery response — documentation, final evidence, commit/push only after acceptance.

## Log
- L1: User requested Phase 3 implementation and completion with all thirteen sections in the session prompt; exact contractual fragments are quoted above. The full original request is retained verbatim below; Engram unavailable, mirror pending.
- L2: Clean main abf493e equals origin/main after successful escalated fetch; new requested branch created. RDD globally off, unchanged. CodeGraph synced; explorer mapped existing pipeline and private schemas. No reusable validation/final event cache exists; one new original-source scan needed.
- L3: Extraction rather than callback chosen: data.py owns shared deterministic states; EDA remains compatible. Seven existing signals, no learned transformations or new dependencies. Private CSVs plus integrity manifest; validation labels isolated and final labels ignored. Forecast exceeds advisory line budget; user explicitly requests one final commit and no automatic PR, so preserve one coherent single-branch delivery.

### L1 — Original authorized request (verbatim)

$retention-stage

# Retention Lab — Phase 3: Reproducible Feature Engineering

Actúa como Senior Data Scientist, Machine Learning Engineer y mentor técnico.

Quiero **implementar y completar la Fase 3 de Retention Lab**, trabajando en una rama nueva, y realizar **commit y push al remoto cuando todos los criterios de aceptación estén satisfechos**.

No realices merge a `main` ni comiences la Fase 4.

## 1. Contexto y requisitos previos

Lee íntegramente:

- `AGENTS.md`
- `PROJECT.md`
- `ROADMAP.md`
- `PROGRESS.md`
- `docs/problem_definition.md`
- `docs/methodology.md`

Inspecciona los scripts, módulos, tests y artefactos de las fases anteriores antes de proponer modificaciones.

Comprueba que `main` contiene la Fase 2 terminada y publicada.

El proyecto utiliza el contrato `RESTRICTED GO`: evaluación retrospectiva de una única cohorte de febrero de 2017. No representa un despliegue histórico real ni valida generalización temporal entre meses.

Las condiciones aprobadas son:

- Etiquetas: `train.csv`.
- Eventos predictivos: `transactions.csv`, exclusivamente la versión original.
- Cutoff: `2017-01-31`.
- Fecha conceptual de predicción: `2017-02-01`.
- Elegibilidad: exactamente la especificada en la Fase 1.
- Particiones: SHA-256 de `retention-lab-feb2017-v1|` + `msno`, entero módulo 10.
- Buckets 0–5: entrenamiento.
- Buckets 6–7: validación.
- Buckets 8–9: evaluación final.
- Población aprobada: 874.580 usuarios etiquetados, con un candidato excluido por falta de etiqueta.
- Distribución verificada: 523.998 entrenamiento, 175.651 validación y 174.931 evaluación final.

No alteres este contrato sin justificarlo y detenerte para solicitar aprobación.

## 2. Gestión de Git

Antes de implementar:

1. Verifica que el working tree esté limpio.
2. Ejecuta `git fetch origin`.
3. Comprueba que `main` está actualizado respecto a `origin/main`.
4. Crea una rama nueva desde `main`:

   `feat/kkbox-feature-engineering`

5. Realiza todo el trabajo exclusivamente en esa rama.

No modifiques directamente `main`.

No sobrescribas trabajo local existente ni utilices `reset --hard` para resolver problemas de sincronización.

## 3. Objetivo de la Fase 3

Crear un proceso reproducible que transforme los eventos originales de KKBOX en una tabla de características por suscriptor válida para entrenamiento y validación posterior.

La salida debe tener:

- Una fila por usuario elegible.
- Variables calculadas exclusivamente con información hasta el cutoff.
- Partición reproducible y consistente con la Fase 2.
- Esquema documentado.
- Controles de integridad y leakage.
- Formato apto para su consumo posterior por scikit-learn.

**Todavía no hay que entrenar ni seleccionar modelos.**

## 4. Reutilizar el trabajo existente

Revisa específicamente:

- `src/retention_lab/eda_prepare.py`
- `src/retention_lab/eda.py`
- `scripts/prepare_kkbox_eda.py`
- `tests/test_prepare_kkbox_eda.py`

Evita crear una segunda implementación independiente de elegibilidad, deduplicación, estados diarios o particionado.

Reutiliza o extrae funciones comunes cuando sea necesario, manteniendo el comportamiento aprobado de las fases anteriores.

Si decides refactorizar, exige pruebas que demuestren equivalencia de resultados y compatibilidad con la reproducción del EDA existente.

No reproceses 21 millones de transacciones repetidamente si puedes aprovechar de forma segura artefactos privados ya verificados.

## 5. Características predictivas

Parte de las señales justificadas por el EDA:

- Estado observado de renovación automática.
- Duración de historial transaccional observado.
- Número de transacciones recientes.
- Frecuencia de transacciones históricas.
- Duración del plan registrado.
- Importe registrado del último evento.
- Cambios observados en renovación automática.
- Otras variables sencillas justificadas por los hallazgos de Fase 2.

Para cada característica:

1. Define qué representa.
2. Identifica sus columnas originales.
3. Explica cómo se calcula.
4. Demuestra que es cutoff-safe.
5. Documenta sus valores faltantes y casos ambiguos.
6. Justifica por qué puede ser útil.

Mantén el número de variables pequeño y razonable.

No añadas decenas de agregados temporales, variables redundantes o transformaciones complejas por defecto.

No utilices `user_logs`, `members`, archivos v2, variables posteriores al cutoff ni identificadores personales como características predictivas.

## 6. Preparación de entrenamiento, validación y holdout

Genera artefactos privados reproducibles para las tres particiones respetando la siguiente regla:

**Entrenamiento:**
- Puede incluir sus etiquetas.
- Puede utilizarse para desarrollar y estudiar características.

**Validación:**
- Puede incluir etiquetas únicamente en un artefacto privado separado y controlado, preparado para su utilización posterior en la selección de modelos.
- No utilices esas etiquetas para seleccionar características o ajustar decisiones durante esta fase.

**Evaluación final:**
- Prepara únicamente características y claves de unión necesarias.
- No leas, interpretes, exportes ni agregues etiquetas finales.
- No generes prevalencia, métricas ni análisis del conjunto final.

Separa las claves técnicas de las variables predictivas.

Mantén los datos individuales en `data/processed/` o un directorio privado equivalente ignorado por Git.

Los artefactos publicados deben contener solamente esquemas, configuración y agregados seguros.

## 7. Transformaciones y valores faltantes

Implementa una política explícita para:

- Valores numéricos faltantes.
- Variables categóricas.
- Estados diarios ambiguos.
- Fechas excepcionales.
- Duplicados exactos.
- Tipos de datos.
- Registros inconsistentes.

Distingue claramente entre:

- Ingeniería de características determinista a partir de eventos.
- Transformaciones que aprenden parámetros del entrenamiento, como imputación estadística, escalado o codificación categórica.

**No ajustes todavía escaladores, imputadores estadísticos ni codificadores utilizando entrenamiento y validación conjuntamente.**

Si estas transformaciones dependen de parámetros aprendidos, define su contrato para Fase 4, donde se ajustarán exclusivamente sobre entrenamiento.

Prefiere reglas simples y conservadoras antes que imputaciones arbitrarias.

## 8. Arquitectura y entregables

Mantén la arquitectura mínima.

Utiliza, si encajan con el código actual:

- `src/retention_lab/data.py`
- `src/retention_lab/features.py`
- Un script CLI pequeño para producir las tablas.
- Tests unitarios y de integración con datos sintéticos.
- Documentación de esquema y procedencia de características.

No crees clases, frameworks ni configuraciones extensas salvo necesidad demostrada.

El código reutilizable debe estar en `src/retention_lab/`, no solamente en notebooks.

No crees otro notebook exploratorio salvo que sea imprescindible.

Documenta los comandos necesarios para regenerar las tablas sin publicar los datos originales.

## 9. Tests y comprobaciones obligatorias

Diseña pruebas que cubran:

1. Una fila por usuario.
2. Población y particiones idénticas a Fase 2.
3. Ningún evento posterior al cutoff afecta a las características.
4. Ninguna característica contiene el target ni identificadores.
5. Ausencia de solapamiento entre particiones.
6. Tratamiento determinista de duplicados.
7. Resolución conservadora de eventos del mismo día.
8. Comportamiento ante valores faltantes e inválidos.
9. Reproducibilidad ante reordenamiento de filas cuando el orden no tiene significado temporal.
10. Resultados idénticos con las mismas fuentes y configuración.
11. Ningún acceso a etiquetas del holdout final.
12. Compatibilidad con el EDA ya publicado.

Utiliza fixtures sintéticas pequeñas para pruebas de lógica y ejecuta las verificaciones pertinentes con los archivos reales disponibles localmente.

Distingue claramente tests sintéticos de comprobaciones sobre los datos reales.

No afirmes haber verificado algo que no hayas ejecutado.

## 10. Documentación y progreso

Actualiza:

- `docs/methodology.md` con el esquema y el protocolo de features, o crea un documento específico si así resulta más claro.
- `PROGRESS.md` con tareas completadas, decisiones, verificaciones, limitaciones y siguiente trabajo.
- `ROADMAP.md` para reflejar la finalización únicamente si los criterios se han cumplido.
- `README.md` si es necesario para reproducir los nuevos scripts.

Conserva las limitaciones existentes del benchmark retrospectivo.

No alteres la pregunta principal de Retention Lab ni añadas afirmaciones de impacto causal.

## 11. Definition of Done

La Fase 3 puede considerarse terminada cuando:

- Las tablas de características son reproducibles.
- Se conserva exactamente la definición de elegibilidad.
- Se utilizan exclusivamente eventos anteriores o iguales al 31/01/2017.
- Las particiones siguen siendo las aprobadas.
- El test final permanece sin etiquetas consultadas.
- Las variables tienen procedencia y significado documentados.
- Los valores faltantes y casos ambiguos se tratan de forma explícita.
- Los tests pasan.
- La preparación funciona con los archivos reales, cuando están disponibles.
- Los artefactos privados están correctamente ignorados por Git.
- El EDA anterior continúa siendo reproducible.

No consideres la fase terminada únicamente porque se hayan creado archivos.

Si detectas un bloqueo metodológico, una incompatibilidad con la Fase 2 o un problema de privacidad, no fuerces su cierre.

## 12. Commit y push al finalizar

Si todos los criterios se cumplen:

1. Marca la Fase 3 como `DONE` en `PROGRESS.md` y actualiza el roadmap.
2. Comprueba `git status` y `git diff --check`.
3. Ejecuta las pruebas necesarias.
4. Revisa los archivos staged para evitar datos privados, identificadores, secretos y binarios grandes.
5. Crea el commit:

   `feat(data): build reproducible cutoff-safe churn features`

6. Publica la rama:

   `git push -u origin feat/kkbox-feature-engineering`

7. Verifica que `origin/feat/kkbox-feature-engineering` apunta al commit publicado.

No hagas merge a `main`.
No crees una pull request automáticamente.
No comiences la Fase 4.

Si el trabajo no está completo, explica lo pendiente y no publiques un commit etiquetado como finalización satisfactoria.

## 13. Informe final

Entrega en español:

1. Rama de trabajo y commit final.
2. Archivos creados o modificados.
3. Tabla de features con nombre, definición, origen y riesgos.
4. Usuarios obtenidos por partición.
5. Política de missing values y categorías.
6. Pruebas ejecutadas y resultados.
7. Verificaciones de reproducibilidad.
8. Comprobaciones de privacidad y leakage.
9. Limitaciones que persisten.
10. Estado real de la Fase 3.
11. URL de la rama y SHA remoto.
12. Recomendaciones para la revisión previa al merge.

Explica qué partes de ingeniería de características conviene entender especialmente para defender el proyecto en una entrevista.

**Prioridad:** metodología correcta, código simple, reutilización del trabajo previo y capacidad de terminar. No avances a modelado sin autorización.

### L4 — Final proof and retained limitations

41 tests passed; independent differential and isolation probes passed and parent
reran them in fresh scratch. Real counts are exactly 523998/175651/174931 with
one exclusion; real EDA reconstruction is byte-identical in all four artifacts.
Two clean notebook kernels reproduce text/figures. Real feature cold build once,
cache verified repeatedly (not two real cold builds). A permission-check update
landed while the first real process was running: cache refused its old 0755
directory; parent explicitly tightened only that generated directory to 0700,
then cache passed without byte changes. See PROGRESS.md for exact timings/hashes.
Source isolation is partition-gated CSV evaluation, not denial of raw byte reads.
RDD off; no native review or switch changes. Engram mirror remains unavailable.
The initial extraction and task-file creation were in the same tool batch with
extraction first, contrary to the track-before-write ordering; no scope or data
contract was inferred from that ordering. No claim of strict ordering compliance.
Completion commit identity is supplied by the final delivery response (cannot be
embedded in its own bytes); all tasks belong to that one requested work unit.
