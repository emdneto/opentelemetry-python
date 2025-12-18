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
    BatchLogRecordProcessor,
    InMemoryLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.resources import Resource

resource = Resource(
    {
        "service.name": "A123456789",
        "service.version": "1.34567890",
        "service.instance.id": "123ab456-a123-12ab-12ab-12340a1abc12",
    }
)

# Simple processor setup
simple_exporter = InMemoryLogRecordExporter()
simple_provider = LoggerProvider(resource=resource)
simple_provider.add_log_record_processor(
    SimpleLogRecordProcessor(simple_exporter)
)
simple_logger = simple_provider.get_logger("simple_logger")

# Batch processor setup
batch_exporter = InMemoryLogRecordExporter()
batch_provider = LoggerProvider(resource=resource)
batch_provider.add_log_record_processor(
    BatchLogRecordProcessor(batch_exporter)
)
batch_logger = batch_provider.get_logger("batch_logger")


@pytest.mark.parametrize("num_attributes", [0, 1, 3, 5, 10])
def test_simple_processor_emit(benchmark, num_attributes):
    attributes = {f"key{i}": f"value{i}" for i in range(num_attributes)}

    def benchmark_emit():
        simple_logger.emit(
            severity_number=SeverityNumber.INFO,
            body="benchmark log message",
            attributes=attributes,
        )

    benchmark(benchmark_emit)


@pytest.mark.parametrize("num_attributes", [0, 1, 3, 5, 10])
def test_batch_processor_emit(benchmark, num_attributes):
    attributes = {f"key{i}": f"value{i}" for i in range(num_attributes)}

    def benchmark_emit():
        batch_logger.emit(
            severity_number=SeverityNumber.INFO,
            body="benchmark log message",
            attributes=attributes,
        )

    benchmark(benchmark_emit)
