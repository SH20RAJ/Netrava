# ADR-002: Universal Event Schema using CNCF CloudEvents 1.0

## Status
Accepted

## Context
In a multi-agency surveillance platform, AI detectors, ANPR workers, camera adapters, and alert engines must exchange messages without tight coupling to any specific AI vendor or proprietary hardware format.

## Decision
We adopted the **CNCF CloudEvents 1.0** specification for all telemetry and analytics events traversing Netrava:
- Structured type taxonomy: `in.gov.gujarat.police.netrava.<entity>.<action>`
- Standard attributes: `id`, `source`, `subject`, `time`, `datacontenttype`, `data`
- Transport neutrality: Compatible with Apache Kafka, Redpanda, Redis Streams, or REST webhooks.

## Consequences
- Clean separation between video acquisition, model inference, and event consumption.
- Eliminates vendor lock-in; any third-party AI provider can publish to the fabric by conforming to the schema.
