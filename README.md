# sport-code

Pipeline para extraer, limpiar, estructurar y convertir conocimiento deportivo en datos y preguntas.

## Estructura

- `config/`: configuracion de deportes y del pipeline.
- `data/`: datos fuente y artefactos generados.
- `pipeline/`: etapas ejecutables del procesamiento.
- `src/sport_code/`: paquete Python principal.
- `tests/`: pruebas automatizadas.
- `app/`: aplicacion de consumo o exploracion.

## Instalacion

```bash
python -m pip install -e .
```

## Desarrollo

```bash
pytest
```
