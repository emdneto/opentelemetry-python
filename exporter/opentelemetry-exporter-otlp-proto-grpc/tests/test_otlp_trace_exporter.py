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

# pylint: disable=too-many-lines

import os
from unittest import TestCase
from unittest.mock import Mock, PropertyMock, patch

from grpc import ChannelCredentials, Compression

from opentelemetry.attributes import BoundedAttributes
from opentelemetry.exporter.otlp.proto.common._internal import (
    _encode_key_value,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.version import __version__
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)
from opentelemetry.proto.common.v1.common_pb2 import (
    AnyValue,
    ArrayValue,
    KeyValue,
)
from opentelemetry.proto.common.v1.common_pb2 import (
    InstrumentationScope as PB2InstrumentationScope,
)
from opentelemetry.proto.resource.v1.resource_pb2 import (
    Resource as OTLPResource,
)
from opentelemetry.proto.trace.v1.trace_pb2 import (
    ResourceSpans,
    ScopeSpans,
    Status,
)
from opentelemetry.proto.trace.v1.trace_pb2 import Span as OTLPSpan
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_COMPRESSION,
    OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE,
    OTEL_EXPORTER_OTLP_TRACES_CLIENT_CERTIFICATE,
    OTEL_EXPORTER_OTLP_TRACES_CLIENT_KEY,
    OTEL_EXPORTER_OTLP_TRACES_COMPRESSION,
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
    OTEL_EXPORTER_OTLP_TRACES_HEADERS,
    OTEL_EXPORTER_OTLP_TRACES_INSECURE,
    OTEL_EXPORTER_OTLP_TRACES_TIMEOUT,
)
from opentelemetry.sdk.resources import Resource as SDKResource
from opentelemetry.sdk.trace import Status as SDKStatus
from opentelemetry.sdk.trace import StatusCode as SDKStatusCode
from opentelemetry.sdk.trace import TracerProvider, _Span
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.test.spantestutil import (
    get_span_with_dropped_attributes_events_links,
)

THIS_DIR = os.path.dirname(__file__)


class TestOTLPSpanExporter(TestCase):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        tracer_provider = TracerProvider()
        self.exporter = OTLPSpanExporter(insecure=True)
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = tracer_provider.get_tracer(__name__)

        event_mock = Mock(
            **{
                "timestamp": 1591240820506462784,
                "attributes": BoundedAttributes(
                    attributes={"a": 1, "b": False}
                ),
            }
        )

        type(event_mock).name = PropertyMock(return_value="a")
        type(event_mock).dropped_attributes = PropertyMock(return_value=0)
        self.span = _Span(
            "a",
            context=Mock(
                **{
                    "trace_state": {"a": "b", "c": "d"},
                    "span_id": 10217189687419569865,
                    "trace_id": 67545097771067222548457157018666467027,
                }
            ),
            resource=SDKResource({"a": 1, "b": False}),
            parent=Mock(**{"span_id": 12345}),
            attributes=BoundedAttributes(attributes={"a": 1, "b": True}),
            events=[event_mock],
            links=[
                Mock(
                    **{
                        "context.trace_id": 1,
                        "context.span_id": 2,
                        "attributes": BoundedAttributes(
                            attributes={"a": 1, "b": False}
                        ),
                        "dropped_attributes": 0,
                        "kind": OTLPSpan.SpanKind.SPAN_KIND_INTERNAL,  # pylint: disable=no-member
                    }
                )
            ],
            instrumentation_scope=InstrumentationScope(
                name="name", version="version"
            ),
        )

        self.span2 = _Span(
            "b",
            context=Mock(
                **{
                    "trace_state": {"a": "b", "c": "d"},
                    "span_id": 10217189687419569865,
                    "trace_id": 67545097771067222548457157018666467027,
                }
            ),
            resource=SDKResource({"a": 2, "b": False}),
            parent=Mock(**{"span_id": 12345}),
            instrumentation_scope=InstrumentationScope(
                name="name", version="version"
            ),
        )

        self.span3 = _Span(
            "c",
            context=Mock(
                **{
                    "trace_state": {"a": "b", "c": "d"},
                    "span_id": 10217189687419569865,
                    "trace_id": 67545097771067222548457157018666467027,
                }
            ),
            resource=SDKResource({"a": 1, "b": False}),
            parent=Mock(**{"span_id": 12345}),
            instrumentation_scope=InstrumentationScope(
                name="name2", version="version2"
            ),
        )

        self.span.start()
        self.span.end()
        self.span2.start()
        self.span2.end()
        self.span3.start()
        self.span3.end()

    def test_exporting(self):
        # pylint: disable=protected-access
        self.assertEqual(self.exporter._exporting, "traces")

    @patch.dict(
        "os.environ",
        {
            OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: "collector:4317",
            OTEL_EXPORTER_OTLP_TRACES_HEADERS: " key1=value1,KEY2 = value=2",
            OTEL_EXPORTER_OTLP_TRACES_TIMEOUT: "10",
            OTEL_EXPORTER_OTLP_TRACES_COMPRESSION: "gzip",
        },
    )
    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.exporter.OTLPExporterMixin.__init__"
    )
    def test_env_variables(self, mock_exporter_mixin):
        OTLPSpanExporter()
        self.assertTrue(len(mock_exporter_mixin.call_args_list) == 1)
        _, kwargs = mock_exporter_mixin.call_args_list[0]
        self.assertEqual(kwargs["endpoint"], "collector:4317")
        self.assertEqual(kwargs["headers"], " key1=value1,KEY2 = value=2")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["compression"], Compression.Gzip)
        self.assertIsNone(kwargs["credentials"])

    @patch.dict(
        "os.environ",
        {
            OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: "collector:4317",
            OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE: THIS_DIR
            + "/fixtures/test.cert",
            OTEL_EXPORTER_OTLP_TRACES_CLIENT_CERTIFICATE: THIS_DIR
            + "/fixtures/test-client-cert.pem",
            OTEL_EXPORTER_OTLP_TRACES_CLIENT_KEY: THIS_DIR
            + "/fixtures/test-client-key.pem",
            OTEL_EXPORTER_OTLP_TRACES_HEADERS: " key1=value1,KEY2 = value=2",
            OTEL_EXPORTER_OTLP_TRACES_TIMEOUT: "10",
            OTEL_EXPORTER_OTLP_TRACES_COMPRESSION: "gzip",
        },
    )
    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.exporter.OTLPExporterMixin.__init__"
    )
    def test_env_variables_with_client_certificates(self, mock_exporter_mixin):
        OTLPSpanExporter()

        self.assertTrue(len(mock_exporter_mixin.call_args_list) == 1)
        _, kwargs = mock_exporter_mixin.call_args_list[0]
        self.assertEqual(kwargs["endpoint"], "collector:4317")
        self.assertEqual(kwargs["headers"], " key1=value1,KEY2 = value=2")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["compression"], Compression.Gzip)
        self.assertIsNotNone(kwargs["credentials"])
        self.assertIsInstance(kwargs["credentials"], ChannelCredentials)

    @patch.dict(
        "os.environ",
        {
            OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: "collector:4317",
            OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE: THIS_DIR
            + "/fixtures/test.cert",
            OTEL_EXPORTER_OTLP_TRACES_HEADERS: " key1=value1,KEY2 = value=2",
            OTEL_EXPORTER_OTLP_TRACES_TIMEOUT: "10",
            OTEL_EXPORTER_OTLP_TRACES_COMPRESSION: "gzip",
        },
    )
    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.exporter.OTLPExporterMixin.__init__"
    )
    @patch("logging.Logger.error")
    def test_env_variables_with_only_certificate(
        self, mock_logger_error, mock_exporter_mixin
    ):
        OTLPSpanExporter()

        self.assertTrue(len(mock_exporter_mixin.call_args_list) == 1)
        _, kwargs = mock_exporter_mixin.call_args_list[0]
        self.assertEqual(kwargs["endpoint"], "collector:4317")
        self.assertEqual(kwargs["headers"], " key1=value1,KEY2 = value=2")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["compression"], Compression.Gzip)
        self.assertIsNotNone(kwargs["credentials"])
        self.assertIsInstance(kwargs["credentials"], ChannelCredentials)

        mock_logger_error.assert_not_called()

    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.exporter.ssl_channel_credentials"
    )
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.secure_channel")
    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter._stub"
    )
    # pylint: disable=unused-argument
    def test_no_credentials_error(
        self, mock_ssl_channel, mock_secure, mock_stub
    ):
        OTLPSpanExporter(insecure=False)
        self.assertTrue(mock_ssl_channel.called)

    @patch.dict(
        "os.environ",
        {OTEL_EXPORTER_OTLP_TRACES_HEADERS: " key1=value1,KEY2 = VALUE=2 "},
    )
    @patch(
        "opentelemetry.exporter.otlp.proto.grpc.exporter.ssl_channel_credentials"
    )
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.secure_channel")
    # pylint: disable=unused-argument
    def test_otlp_headers_from_env(self, mock_ssl_channel, mock_secure):
        exporter = OTLPSpanExporter()
        # pylint: disable=protected-access
        self.assertEqual(
            exporter._headers,
            (
                ("key1", "value1"),
                ("key2", "VALUE=2"),
            ),
        )
        exporter = OTLPSpanExporter(
            headers=(("key3", "value3"), ("key4", "value4"))
        )
        # pylint: disable=protected-access
        self.assertEqual(
            exporter._headers,
            (
                ("key3", "value3"),
                ("key4", "value4"),
            ),
        )
        exporter = OTLPSpanExporter(
            headers={"key5": "value5", "key6": "value6"}
        )
        # pylint: disable=protected-access
        self.assertEqual(
            exporter._headers,
            (
                ("key5", "value5"),
                ("key6", "value6"),
            ),
        )

    @patch.dict(
        "os.environ",
        {OTEL_EXPORTER_OTLP_TRACES_INSECURE: "True"},
    )
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.insecure_channel")
    # pylint: disable=unused-argument
    def test_otlp_insecure_from_env(self, mock_insecure):
        OTLPSpanExporter()
        # pylint: disable=protected-access
        self.assertTrue(mock_insecure.called)
        self.assertEqual(
            1,
            mock_insecure.call_count,
            f"expected {mock_insecure} to be called",
        )

    # pylint: disable=no-self-use
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.insecure_channel")
    @patch.dict("os.environ", {OTEL_EXPORTER_OTLP_COMPRESSION: "gzip"})
    def test_otlp_exporter_otlp_compression_kwarg(self, mock_insecure_channel):
        """Specifying kwarg should take precedence over env"""
        OTLPSpanExporter(insecure=True, compression=Compression.NoCompression)
        mock_insecure_channel.assert_called_once_with(
            "localhost:4317",
            compression=Compression.NoCompression,
            options=(
                (
                    "grpc.primary_user_agent",
                    "OTel-OTLP-Exporter-Python/" + __version__,
                ),
            ),
        )

    # pylint: disable=no-self-use
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.insecure_channel")
    @patch.dict(
        "os.environ",
        {OTEL_EXPORTER_OTLP_TRACES_COMPRESSION: "gzip"},
    )
    def test_otlp_exporter_otlp_compression_precendence(
        self, mock_insecure_channel
    ):
        """OTEL_EXPORTER_OTLP_TRACES_COMPRESSION as higher priority than
        OTEL_EXPORTER_OTLP_COMPRESSION
        """
        OTLPSpanExporter(insecure=True)
        mock_insecure_channel.assert_called_once_with(
            "localhost:4317",
            compression=Compression.Gzip,
            options=(
                (
                    "grpc.primary_user_agent",
                    "OTel-OTLP-Exporter-Python/" + __version__,
                ),
            ),
        )

    # pylint: disable=no-self-use
    @patch("opentelemetry.exporter.otlp.proto.grpc.exporter.insecure_channel")
    def test_otlp_exporter_otlp_channel_options_kwarg(
        self, mock_insecure_channel
    ):
        OTLPSpanExporter(insecure=True, channel_options=(("some", "options"),))
        mock_insecure_channel.assert_called_once_with(
            "localhost:4317",
            compression=Compression.NoCompression,
            options=(
                (
                    "grpc.primary_user_agent",
                    "OTel-OTLP-Exporter-Python/" + __version__,
                ),
                ("some", "options"),
            ),
        )

    def test_translate_spans(self):
        expected = ExportTraceServiceRequest(
            resource_spans=[
                ResourceSpans(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_spans=[
                        ScopeSpans(
                            scope=PB2InstrumentationScope(
                                name="name", version="version"
                            ),
                            spans=[
                                OTLPSpan(
                                    # pylint: disable=no-member
                                    name="a",
                                    start_time_unix_nano=self.span.start_time,
                                    end_time_unix_nano=self.span.end_time,
                                    trace_state="a=b,c=d",
                                    span_id=int.to_bytes(
                                        10217189687419569865, 8, "big"
                                    ),
                                    trace_id=int.to_bytes(
                                        67545097771067222548457157018666467027,
                                        16,
                                        "big",
                                    ),
                                    parent_span_id=(
                                        b"\000\000\000\000\000\00009"
                                    ),
                                    kind=(
                                        OTLPSpan.SpanKind.SPAN_KIND_INTERNAL
                                    ),
                                    attributes=[
                                        KeyValue(
                                            key="a",
                                            value=AnyValue(int_value=1),
                                        ),
                                        KeyValue(
                                            key="b",
                                            value=AnyValue(bool_value=True),
                                        ),
                                    ],
                                    events=[
                                        OTLPSpan.Event(
                                            name="a",
                                            time_unix_nano=1591240820506462784,
                                            attributes=[
                                                KeyValue(
                                                    key="a",
                                                    value=AnyValue(
                                                        int_value=1
                                                    ),
                                                ),
                                                KeyValue(
                                                    key="b",
                                                    value=AnyValue(
                                                        bool_value=False
                                                    ),
                                                ),
                                            ],
                                        )
                                    ],
                                    status=Status(code=0, message=""),
                                    links=[
                                        OTLPSpan.Link(
                                            trace_id=int.to_bytes(
                                                1, 16, "big"
                                            ),
                                            span_id=int.to_bytes(2, 8, "big"),
                                            attributes=[
                                                KeyValue(
                                                    key="a",
                                                    value=AnyValue(
                                                        int_value=1
                                                    ),
                                                ),
                                                KeyValue(
                                                    key="b",
                                                    value=AnyValue(
                                                        bool_value=False
                                                    ),
                                                ),
                                            ],
                                            flags=0x300,
                                        )
                                    ],
                                    flags=0x300,
                                )
                            ],
                        )
                    ],
                ),
            ]
        )

        # pylint: disable=protected-access
        self.assertEqual(expected, self.exporter._translate_data([self.span]))

    def test_translate_spans_multi(self):
        expected = ExportTraceServiceRequest(
            resource_spans=[
                ResourceSpans(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=1)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_spans=[
                        ScopeSpans(
                            scope=PB2InstrumentationScope(
                                name="name", version="version"
                            ),
                            spans=[
                                OTLPSpan(
                                    # pylint: disable=no-member
                                    name="a",
                                    start_time_unix_nano=self.span.start_time,
                                    end_time_unix_nano=self.span.end_time,
                                    trace_state="a=b,c=d",
                                    span_id=int.to_bytes(
                                        10217189687419569865, 8, "big"
                                    ),
                                    trace_id=int.to_bytes(
                                        67545097771067222548457157018666467027,
                                        16,
                                        "big",
                                    ),
                                    parent_span_id=(
                                        b"\000\000\000\000\000\00009"
                                    ),
                                    kind=(
                                        OTLPSpan.SpanKind.SPAN_KIND_INTERNAL
                                    ),
                                    attributes=[
                                        KeyValue(
                                            key="a",
                                            value=AnyValue(int_value=1),
                                        ),
                                        KeyValue(
                                            key="b",
                                            value=AnyValue(bool_value=True),
                                        ),
                                    ],
                                    events=[
                                        OTLPSpan.Event(
                                            name="a",
                                            time_unix_nano=1591240820506462784,
                                            attributes=[
                                                KeyValue(
                                                    key="a",
                                                    value=AnyValue(
                                                        int_value=1
                                                    ),
                                                ),
                                                KeyValue(
                                                    key="b",
                                                    value=AnyValue(
                                                        bool_value=False
                                                    ),
                                                ),
                                            ],
                                        )
                                    ],
                                    status=Status(code=0, message=""),
                                    links=[
                                        OTLPSpan.Link(
                                            trace_id=int.to_bytes(
                                                1, 16, "big"
                                            ),
                                            span_id=int.to_bytes(2, 8, "big"),
                                            attributes=[
                                                KeyValue(
                                                    key="a",
                                                    value=AnyValue(
                                                        int_value=1
                                                    ),
                                                ),
                                                KeyValue(
                                                    key="b",
                                                    value=AnyValue(
                                                        bool_value=False
                                                    ),
                                                ),
                                            ],
                                            flags=0x300,
                                        )
                                    ],
                                    flags=0x300,
                                )
                            ],
                        ),
                        ScopeSpans(
                            scope=PB2InstrumentationScope(
                                name="name2", version="version2"
                            ),
                            spans=[
                                OTLPSpan(
                                    # pylint: disable=no-member
                                    name="c",
                                    start_time_unix_nano=self.span3.start_time,
                                    end_time_unix_nano=self.span3.end_time,
                                    trace_state="a=b,c=d",
                                    span_id=int.to_bytes(
                                        10217189687419569865, 8, "big"
                                    ),
                                    trace_id=int.to_bytes(
                                        67545097771067222548457157018666467027,
                                        16,
                                        "big",
                                    ),
                                    parent_span_id=(
                                        b"\000\000\000\000\000\00009"
                                    ),
                                    kind=(
                                        OTLPSpan.SpanKind.SPAN_KIND_INTERNAL
                                    ),
                                    status=Status(code=0, message=""),
                                    flags=0x300,
                                )
                            ],
                        ),
                    ],
                ),
                ResourceSpans(
                    resource=OTLPResource(
                        attributes=[
                            KeyValue(key="a", value=AnyValue(int_value=2)),
                            KeyValue(
                                key="b", value=AnyValue(bool_value=False)
                            ),
                        ]
                    ),
                    scope_spans=[
                        ScopeSpans(
                            scope=PB2InstrumentationScope(
                                name="name", version="version"
                            ),
                            spans=[
                                OTLPSpan(
                                    # pylint: disable=no-member
                                    name="b",
                                    start_time_unix_nano=self.span2.start_time,
                                    end_time_unix_nano=self.span2.end_time,
                                    trace_state="a=b,c=d",
                                    span_id=int.to_bytes(
                                        10217189687419569865, 8, "big"
                                    ),
                                    trace_id=int.to_bytes(
                                        67545097771067222548457157018666467027,
                                        16,
                                        "big",
                                    ),
                                    parent_span_id=(
                                        b"\000\000\000\000\000\00009"
                                    ),
                                    kind=(
                                        OTLPSpan.SpanKind.SPAN_KIND_INTERNAL
                                    ),
                                    status=Status(code=0, message=""),
                                    flags=0x300,
                                )
                            ],
                        )
                    ],
                ),
            ]
        )

        # pylint: disable=protected-access
        self.assertEqual(
            expected,
            self.exporter._translate_data([self.span, self.span2, self.span3]),
        )

    def _check_translated_status(
        self,
        translated: ExportTraceServiceRequest,
        code_expected: Status,
    ):
        status = translated.resource_spans[0].scope_spans[0].spans[0].status

        self.assertEqual(
            status.code,
            code_expected,
        )

    def test_span_status_translate(self):
        # pylint: disable=protected-access,no-member
        unset = SDKStatus(status_code=SDKStatusCode.UNSET)
        ok = SDKStatus(status_code=SDKStatusCode.OK)
        error = SDKStatus(status_code=SDKStatusCode.ERROR)
        unset_translated = self.exporter._translate_data(
            [_create_span_with_status(unset)]
        )
        ok_translated = self.exporter._translate_data(
            [_create_span_with_status(ok)]
        )
        error_translated = self.exporter._translate_data(
            [_create_span_with_status(error)]
        )
        self._check_translated_status(
            unset_translated,
            Status.STATUS_CODE_UNSET,
        )
        self._check_translated_status(
            ok_translated,
            Status.STATUS_CODE_OK,
        )
        self._check_translated_status(
            error_translated,
            Status.STATUS_CODE_ERROR,
        )

    # pylint:disable=no-member
    def test_translate_key_values(self):
        bool_value = _encode_key_value("bool_type", False)
        self.assertTrue(isinstance(bool_value, KeyValue))
        self.assertEqual(bool_value.key, "bool_type")
        self.assertTrue(isinstance(bool_value.value, AnyValue))
        self.assertFalse(bool_value.value.bool_value)

        str_value = _encode_key_value("str_type", "str")
        self.assertTrue(isinstance(str_value, KeyValue))
        self.assertEqual(str_value.key, "str_type")
        self.assertTrue(isinstance(str_value.value, AnyValue))
        self.assertEqual(str_value.value.string_value, "str")

        int_value = _encode_key_value("int_type", 2)
        self.assertTrue(isinstance(int_value, KeyValue))
        self.assertEqual(int_value.key, "int_type")
        self.assertTrue(isinstance(int_value.value, AnyValue))
        self.assertEqual(int_value.value.int_value, 2)

        double_value = _encode_key_value("double_type", 3.2)
        self.assertTrue(isinstance(double_value, KeyValue))
        self.assertEqual(double_value.key, "double_type")
        self.assertTrue(isinstance(double_value.value, AnyValue))
        self.assertEqual(double_value.value.double_value, 3.2)

        seq_value = _encode_key_value("seq_type", ["asd", "123"])
        self.assertTrue(isinstance(seq_value, KeyValue))
        self.assertEqual(seq_value.key, "seq_type")
        self.assertTrue(isinstance(seq_value.value, AnyValue))
        self.assertTrue(isinstance(seq_value.value.array_value, ArrayValue))

        arr_value = seq_value.value.array_value
        self.assertTrue(isinstance(arr_value.values[0], AnyValue))
        self.assertEqual(arr_value.values[0].string_value, "asd")
        self.assertTrue(isinstance(arr_value.values[1], AnyValue))
        self.assertEqual(arr_value.values[1].string_value, "123")

    def test_dropped_values(self):
        span = get_span_with_dropped_attributes_events_links()
        # pylint:disable=protected-access
        translated = self.exporter._translate_data([span])
        self.assertEqual(
            1,
            translated.resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .dropped_links_count,
        )
        self.assertEqual(
            2,
            translated.resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .dropped_attributes_count,
        )
        self.assertEqual(
            3,
            translated.resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .dropped_events_count,
        )
        self.assertEqual(
            2,
            translated.resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .links[0]
            .dropped_attributes_count,
        )
        self.assertEqual(
            2,
            translated.resource_spans[0]
            .scope_spans[0]
            .spans[0]
            .events[0]
            .dropped_attributes_count,
        )


def _create_span_with_status(status: SDKStatus):
    span = _Span(
        "a",
        context=Mock(
            **{
                "trace_state": {"a": "b", "c": "d"},
                "span_id": 10217189687419569865,
                "trace_id": 67545097771067222548457157018666467027,
            }
        ),
        parent=Mock(**{"span_id": 12345}),
        instrumentation_scope=InstrumentationScope(
            name="name", version="version"
        ),
    )
    span.set_status(status)
    return span
