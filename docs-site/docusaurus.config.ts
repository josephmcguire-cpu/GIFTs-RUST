import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'GIFTs',
  tagline: 'Annex 3 TAC to IWXXM',
  favicon: 'img/favicon.png',

  url: 'https://josephmcguire-cpu.github.io',
  baseUrl: '/GIFTs-RUST/',

  organizationName: 'josephmcguire-cpu',
  projectName: 'GIFTs-RUST',

  onBrokenLinks: 'throw',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: ['@docusaurus/theme-mermaid'],

  markdown: {
    mermaid: true,
  },

  themeConfig: {
    navbar: {
      title: 'GIFTs docs',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://github.com/josephmcguire-cpu/GIFTs-RUST',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} GIFTs documentation. Software is in the public domain; see repository LICENSE.`,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
