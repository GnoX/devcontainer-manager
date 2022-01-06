{% if cookiecutter.dockerfile is not none %}
{{ cookiecutter.dockerfile.content }}

{%- for command in cookiecutter.dockerfile.additional_commands %}
{{ command }}
{%- endfor %}
{% endif %}
