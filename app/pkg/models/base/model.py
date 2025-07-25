"""Base model for all models in API server."""

from __future__ import annotations

import typing
from datetime import date, datetime, time
from typing import Any, TypeVar
from uuid import UUID

import pydantic
from _decimal import Decimal
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ConfigDict, TypeAdapter

__all__ = ["BaseModel", "Model"]

Model = TypeVar("Model", bound="BaseModel")
_T = TypeVar("_T")


class BaseModel(pydantic.BaseModel):
    """Base model for all models in API server."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        coerce_numbers_to_str=True,
    )

    def to_dict(
        self,
        show_secrets: bool = False,
        values: dict[Any, Any] = None,
        **kwargs,
    ) -> dict[Any, Any]:
        """Make a representation model from a class object to Dict object.

        Args:
            show_secrets:
                bool.
                default False.
                Shows secret in dict an object if True.
            values:
                Using an object to write to a Dict object.
            **kwargs:
                Optional arguments to be passed to the Dict object.

        Examples:
            If you don't want to show secret in a dict object,
            then you shouldn't use ``show_secrets`` argument::

                >>> from app.pkg.models.base import BaseModel
                >>> class TestModel(BaseModel):
                ...     some_value: pydantic.SecretStr
                ...     some_value_two: pydantic.SecretBytes
                >>> model = TestModel(some_value="key", some_value_two="value")
                >>> assert isinstance(model.some_value, pydantic.SecretStr)
                >>> assert isinstance(model.some_value_two, pydantic.SecretBytes)
                >>> dict_model = model.to_dict()
                >>> assert isinstance(dict_model["some_value"], str)
                >>> assert isinstance(dict_model["some_value_two"], str)
                >>> print(dict_model["some_value"])
                '**********'
                >>> print(dict_model["some_value_two"])
                '**********'

            If you want to deciphe sensitivity in a dict object,
            then you should use ``show_secrets`` argument::

                >>> from app.pkg.models.base import BaseModel
                >>> class TestModel(BaseModel):
                ...     some_value: pydantic.SecretStr
                ...     some_value_two: pydantic.SecretBytes
                >>> model = TestModel(some_value="key", some_value_two="value")
                >>> assert isinstance(model.some_value, pydantic.SecretStr)
                >>> assert isinstance(model.some_value_two, pydantic.SecretBytes)
                >>> dict_model = model.to_dict(show_secrets=True)
                >>> assert isinstance(dict_model["some_value"], str)
                >>> assert isinstance(dict_model["some_value_two"], str)
                >>> print(dict_model["some_value"])
                'key'
                >>> print(dict_model["some_value_two"])
                'value'

            In such cases, you can use the ``values`` argument for revrite values in
            a dict object::

                >>> from app.pkg.models.base import BaseModel
                >>> class TestModel(BaseModel):
                ...     some_value: pydantic.SecretStr
                ...     some_value_two: pydantic.SecretBytes
                >>> model = TestModel(some_value="key", some_value_two="value")
                >>> assert isinstance(model.some_value, pydantic.SecretStr)
                >>> assert isinstance(model.some_value_two, pydantic.SecretBytes)
                >>> dict_model = model.to_dict(
                ...     show_secrets=True,
                ...     values={"some_value": "value"}
                ... )
                >>> assert isinstance(dict_model["some_value"], str)
                >>> assert isinstance(dict_model["some_value_two"], str)
                >>> print(dict_model["some_value"])
                'value'
                >>> print(dict_model["some_value_two"])
                'value'

        Raises:
            TypeError: If ``values`` are not a Dict object.

        Returns:
            Dict object with reveal password filed.
        """

        values = self.model_dump(**kwargs).items() if not values else values.items()
        r = {}
        for k, v in values:
            v = self.__cast_values(v=v, show_secrets=show_secrets)
            r[k] = v
        return r

    def __cast_values(self, v: _T, show_secrets: bool, **kwargs) -> _T:
        """Cast value for dict object.

        Args:
            v:
                Any value.
            show_secrets:
                If True, then the secret will be revealed.

        Warnings:
            This method is not memory optimized.
        """

        if isinstance(v, (typing.List, typing.Tuple, list, tuple)):
            return [
                self.__cast_values(v=ve, show_secrets=show_secrets, **kwargs)
                for ve in v
            ]

        elif isinstance(v, (pydantic.SecretBytes, pydantic.SecretStr)):
            return self.__cast_secret(v=v, show_secrets=show_secrets)

        elif isinstance(v, (dict, typing.Dict)) and v:
            return self.to_dict(show_secrets=show_secrets, values=v, **kwargs)

        elif isinstance(v, (UUID, Decimal)):
            return str(v)

        elif isinstance(v, (datetime, date, time)):
            return self.__cast_datetime_types(v=v)

        return v

    @staticmethod
    def __cast_datetime_types(v: _T) -> _T:
        """Cast datetime types to str.

        Args:
            v: Any value.

        Returns:
            str value of ``v``.
        """

        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        elif isinstance(v, time):
            return v.strftime("%H:%M:%S")

    @staticmethod
    def __cast_secret(v, show_secrets: bool) -> str:
        """Cast secret value to str.

        Args:
            v: pydantic.Secret* object.
            show_secrets: bool value. If True, then the secret will be revealed.

        Returns: str value of ``v``.
        """

        if isinstance(v, pydantic.SecretBytes):
            return v.get_secret_value().decode() if show_secrets else str(v)
        elif isinstance(v, pydantic.SecretStr):
            return v.get_secret_value() if show_secrets else str(v)

    def delete_attribute(self, attr: str) -> BaseModel:
        """Delete some attribute field from a model.

        Args:
            attr:
                name of field.

        Returns:
            self object.
        """

        delattr(self, attr)
        return self

    def migrate(
        self,
        model: type[BaseModel],
        random_fill: bool = False,
        match_keys: dict[str, str] | None = None,
        extra_fields: dict[str, typing.Any] | None = None,
    ) -> Model:
        """Migrate one model to another ignoring missmatch.

        Args:
            model:
                Heir BaseModel object.
            random_fill:
                If True, then the fields that are not in the
                model will be filled with random values.
            match_keys:
                The keys of this object are the names of the
                fields of the model to which the migration will be made, and the
                values are the names of the fields of the current model.
                Key: name of field in self-model.
                Value: name of field in a target model.
            extra_fields:
                The keys of this object are the names of the
                fields of the model to which the migration will be made, and the
                values are the values of the fields of the current model.

                Key: name of field in a target model.

                Value: value of field in a target model.

        Examples:
            When migrating from model A to model B, the fields that are not
            in model B will be filled with them::

                >>> class A(BaseModel):
                ...     a: int
                ...     b: int
                ...     c: int
                ...     d: int
                >>> class B(BaseModel):
                ...     a: int
                ...     b: int
                ...     c: int
                >>> a = A(a=1, b=2, c=3, d=4)
                >>> a.migrate(model=B)  # B(a=1, b=2, c=3)

            But if you need to fill in the missing fields with a random value,
            then you can use the ``random_fill`` argument::

                >>> class A(BaseModel):
                ...     a: int
                ...     b: int
                ...     c: int
                >>> class B(BaseModel):
                ...     a: int
                ...     aa: int
                ...     b: int
                ...     c: int
                >>> a = A(a=1, b=2, c=3)
                >>> a.migrate(model=B, random_fill=True)  # B(a=1, aa=1011, b=2, c=3)

            If you need to migrate fields with different names, then you can use
            the ``match_keys`` argument::

                >>> class A(BaseModel):
                ...     a: int
                ...     b: int
                ...     c: int
                >>> class B(BaseModel):
                ...     aa: int
                ...     b: int
                ...     c: int
                >>> a = A(a=1, b=2, c=3)
                >>> a.migrate(model=B, match_keys={"aa": "a"})  # B(aa=1, b=2, c=3)

            If you need to add additional fields to the model, then you can use
            the ``extra_fields`` argument::

                >>> class A(BaseModel):
                ...     a: int
                ...     b: int
                >>> class B(BaseModel):
                ...     a: int
                ...     b: int
                ...     c: int
                >>> a = A(a=1, b=2, c=3)
                >>> a.migrate(model=B, extra_fields={"c": 3})  # B(a=1, b=2, c=3)


        Returns:
            pydantic model parsed from ``model``.
        """

        self_dict_model = self.to_dict(show_secrets=True)

        if not match_keys:
            match_keys = {}
        if not extra_fields:
            extra_fields = {}

        for key, value in match_keys.items():
            self_dict_model[key] = self_dict_model.pop(value)

        for key, value in extra_fields.items():
            self_dict_model[key] = value

        adapter = TypeAdapter(model)
        if not random_fill:
            return adapter.validate_python(self_dict_model)

        class Factory(ModelFactory[model]): ...

        return Factory.build(factory_use_construct=True, **self_dict_model)

    @classmethod
    def factory(cls):
        """Create random data for model.
        Examples:
            When you need to create a random model, just use factory function:
                >>> from app.pkg.models import v1 as models
                >>> city = models.City.factory().build()

            If you need to add specific value, use this construction:
                >>> from app.pkg.models import v1 as models
                >>> city = models.City.factory().build(city_code="MSK")
        """

        class Factory(ModelFactory[cls]):
            __use_defaults__ = False

        return Factory
