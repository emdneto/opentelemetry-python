# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    InMemoryLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.resources import Resource

logger_provider = LoggerProvider(
    resource=Resource(
        {
            "service.name": "A123456789",
            "service.version": "1.34567890",
            "service.instance.id": "123ab456-a123-12ab-12ab-12340a1abc12",
        }
    ),
)
exporter = InMemoryLogRecordExporter()
logger_provider.add_log_record_processor(SimpleLogRecordProcessor(exporter))
logger = logger_provider.get_logger("sdk_logger")


def test_simple_emit_log(benchmark):
    def benchmark_emit_log():
        logger.emit(
            severity_number=SeverityNumber.INFO,
            body="benchmark log message",
        )

    benchmark(benchmark_emit_log)


def test_emit_log_with_event_name(benchmark):
    def benchmark_emit_log():
        logger.emit(
            severity_number=SeverityNumber.INFO,
            body="benchmark log message",
            event_name="test.event",
        )

    benchmark(benchmark_emit_log)


@pytest.mark.parametrize("num_attributes", [0, 1, 3, 5, 10])
def test_emit_log_with_attributes(benchmark, num_attributes):
    attributes = {f"key{i}": f"value{i}" for i in range(num_attributes)}

    def benchmark_emit_log():
        logger.emit(
            severity_number=SeverityNumber.INFO,
            body="benchmark log message",
            attributes=attributes,
        )

    benchmark(benchmark_emit_log)


@pytest.mark.parametrize(
    "severity",
    [
        SeverityNumber.DEBUG,
        SeverityNumber.INFO,
        SeverityNumber.WARN,
        SeverityNumber.ERROR,
    ],
)
def test_emit_log_different_severity(benchmark, severity):
    def benchmark_emit_log():
        logger.emit(
            severity_number=severity,
            body="benchmark log message",
        )

    benchmark(benchmark_emit_log)


def test_get_logger(benchmark):
    def benchmark_get_logger():
        logger_provider.get_logger("test_logger")

    benchmark(benchmark_get_logger)


def test_get_logger_with_version(benchmark):
    def benchmark_get_logger():
        logger_provider.get_logger("test_logger", version="1.0.0")

    benchmark(benchmark_get_logger)


def test_get_logger_with_schema_url(benchmark):
    def benchmark_get_logger():
        logger_provider.get_logger(
            "test_logger",
            version="1.0.0",
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )

    benchmark(benchmark_get_logger)
