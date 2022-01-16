{%- if cookiecutter.docker is not none -%}
{%- if cookiecutter.docker.file is not none -%}
{{ cookiecutter.docker.file }}
{%- endif %}

{% for command in cookiecutter.docker.additional_commands -%}
{{ command }}
{% endfor -%}
{%- endif -%}
