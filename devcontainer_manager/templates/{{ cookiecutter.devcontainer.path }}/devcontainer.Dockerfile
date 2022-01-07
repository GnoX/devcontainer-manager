{% if cookiecutter.dockerfile is not none -%}
{% if cookiecutter.dockerfile.file is not none -%}
{{ cookiecutter.dockerfile.file }}
{%- endif %}

{%- for command in cookiecutter.dockerfile.additional_commands %}
{{ command }}
{%- endfor %}
{% endif %}
