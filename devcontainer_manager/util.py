from collections import OrderedDict

import yaml


def setup_yaml():
    mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    yaml.add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_mapping(
            mapping_tag, data.items()
        ),
    )
    yaml.add_constructor(
        mapping_tag,
        lambda loader, node: OrderedDict(loader.construct_pairs(node)),
    )
