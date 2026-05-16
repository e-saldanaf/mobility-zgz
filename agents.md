# Mobility Zaragoza - AI Agents

Este documento define los diferentes Agentes de Inteligencia Artificial (IA) o flujos automatizados que pueden interactuar con los datos del sistema Bizi de Zaragoza generados por este pipeline ETL.

## 🤖 Agentes Propuestos

### 1. Data Quality Agent (Agente de Calidad de Datos)
- **Objetivo:** Monitorear la base de datos en Supabase y los logs del ETL para asegurar que los datos son consistentes. Puede alertar sobre anomalías (ej. caídas repentinas en el total de bicicletas disponibles o estaciones desconectadas).
- **Herramientas:** Lectura de base de datos, análisis de logs de `main.py`.

### 2. Mobility Analyst Agent (Agente Analista de Movilidad)
- **Objetivo:** Traducir preguntas en lenguaje natural a consultas SQL para analizar el estado de las estaciones (ej. *"¿Cuáles son las estaciones con menos bicicletas ahora mismo en la zona centro?"*).
- **Herramientas:** Ejecución de SQL (Solo lectura) en Supabase.

### 3. Alert & Notification Agent (Agente de Alertas)
- **Objetivo:** Notificar proactivamente a los usuarios si una estación que usan habitualmente se queda sin bicicletas o sin anclajes libres durante las horas punta.
- **Herramientas:** Integración con sistemas de mensajería (Telegram, Slack, Email) y lectura de datos en tiempo real.

---

*(Nota: Este es un borrador inicial. Puedes modificarlo para definir reglas para asistentes de código, especificar frameworks como LangChain/CrewAI, o plantear otro tipo de agentes según lo que necesites para el proyecto).*
