import pytest

from makeproto.prototypes2 import BaseMessage, OneOf, ProtoHeader, ProtoOption


class TestProtoMeta:

    def test_missing_protofile(self):
        with pytest.raises(ValueError):
            class TestMissingProtoFile(ProtoHeader):
                _proto_package = "test_package"

    def test_inconsistent_package(self):
        class TestClass1(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "package1"

        with pytest.raises(ValueError):

            class TestClass2(ProtoHeader):
                _proto_file = "file.proto"
                _proto_package = "package2"

    def test_consistent_package(self):
        class TestClass1(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "package1"

        class TestClass2(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "package1"

        try:

            class TestClass3(ProtoHeader):
                _proto_file = "file.proto"
                _proto_package = "package1"

        except ValueError:
            pytest.fail("Inconsistent package raised an error unexpectedly.")


class TestProtoHeader:

    def test_protofile_method(self):
        class TestClass(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "test_package"

        assert TestClass.protofile() == "file.proto"

    def test_package_method(self):
        class TestClass(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "test_package"

        assert TestClass.package() == "test_package"

    def test_comment_method(self):
        class TestClass(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "test_package"
            _comment = "Test comment"

        assert TestClass.comment() == "Test comment"

    def test_options_method(self):
        class TestClass(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "test_package"

        assert isinstance(TestClass.options(), ProtoOption)

    def test_reserved_method(self):
        class TestClass(ProtoHeader):
            _proto_file = "file.proto"
            _proto_package = "test_package"
            _reserved = ["field1", "field2"]

        assert TestClass.reserved() == ["field1", "field2"]


class TestBaseMessage:

    def test_prototype_method(self):
        class TestMessage(BaseMessage):
            _proto_file = "message.proto"
            _proto_package = "test_package"

        assert TestMessage.prototype() == "TestMessage"

    def test_qualified_prototype_method(self):
        class TestMessage(BaseMessage):
            _proto_file = "message.proto"
            _proto_package = "test_package"

        assert TestMessage.qualified_prototype() == "test_package.TestMessage"


class TestOneOf:

    def test_prototype_method_generic(self):
        class TestOneOfString(OneOf[str]):
            _proto_file = "message.proto"
            _proto_package = "test_package"
            _key = "string_key"

        assert TestOneOfString.prototype() == "OneOf[str]"

    def test_key_method(self):
        class TestOneOfString(OneOf[str]):
            _proto_file = "message.proto"
            _proto_package = "test_package"
            _key = "string_key"

        assert TestOneOfString.key() == "string_key"


if __name__ == "__main__":
    pytest.main()
