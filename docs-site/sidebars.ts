import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    { type: 'doc', id: 'index', label: 'Home' },
    { type: 'doc', id: 'trd', label: 'Technical requirements' },
    { type: 'doc', id: 'use-cases', label: 'Use cases' },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/library-encode',
        'workflows/demo-gui',
        'workflows/iwxxmd-daemon',
        'workflows/validation',
        'workflows/e2e',
        'workflows/pipeline-goldens',
      ],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/overview',
        'architecture/dependency-graphs',
        'architecture/gifts-modules',
        'architecture/gifts-products',
        'architecture/metar-pipeline',
        'architecture/validation-modules',
        'architecture/demo-modules',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/repository-layout',
        'reference/validation-layout',
        'reference/xml-config',
        'reference/bulletin-and-distribution',
        'reference/demo-iwxxmd-config',
        'reference/ci-workflows',
        'reference/docker',
        'reference/python-package',
      ],
    },
    {
      type: 'category',
      label: 'Testing',
      items: ['testing/overview', 'testing/pipeline-goldens'],
    },
    { type: 'doc', id: 'contributing', label: 'Contributing' },
  ],
};

export default sidebars;
