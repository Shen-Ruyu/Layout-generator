import os
import xml.dom.minidom as minidom
import argparse

mirror_site_matrix = {
    "alb":"mirrors",
    "yocto": "iip-oss",
    "oe": "iip-oss",
    "linaro": "mirrors",
    "qoriq": "mirrors",
}
alb_upstream = {
    "34.0": "release/bsp34.0-3.2",
    "38.0": "release/bsp38.0-4.0",
    "40.0": "release/bsp40.0-4.0",
    # Upstream for more versions
}
manifest_header = """
<?xml version="1.0" encoding="UTF-8" ?>
  <manifest>
  <remote fetch="ssh://git@github-vni.geo.conti.de/bs-g-nd-ptf-hpc-gen2-mirrors" name="mirrors"/>
  <remote fetch="ssh://git@github-vni.geo.conti.de/supplier-nxp" name="supplier-nxp"/>
  <remote fetch="ssh://git@github-vni.geo.conti.de/iip-oss" name="iip-oss"/>
"""

class ManifestConverter:
    def __init__(self, manifest_path=None, output_path=None, install_path=None, bsp_version=None):
        self.default_xml_path = manifest_path
        self.xml_output_path = output_path
        self.repo_install_path = install_path
        self.bsp_version = bsp_version


    def remove_remote(self):
        dom = minidom.parse(self.default_xml_path)
        manifest = dom.documentElement
        remotes = manifest.getElementsByTagName('remote')

        for remote in remotes:
            manifest.removeChild(remote)
            next_sibling = remote.nextSibling
            if next_sibling and next_sibling.nodeType == minidom.Node.TEXT_NODE and not next_sibling.nodeValue.strip():
                manifest.removeChild(next_sibling)
        return dom
    
    def extract_default_attributes(self, dom):
        """
        Extracts the revision and remote attributes from the default element.
        """
        default = dom.getElementsByTagName('default')
        default_attrs = {'revision': '', 'remote': ''}

        if default:
            default_attrs['revision'] = default[0].getAttribute('revision')
            default_attrs['remote'] = default[0].getAttribute('remote')
        return default_attrs
    

    def replace_project_remote(self, dom, default_attrs):
        manifest = dom.documentElement
        projects = manifest.getElementsByTagName('project')

        for project in projects:
            
            if project.getAttribute('name') == "meta-alb":
                if default_attrs['revision']:
                    project.setAttribute('revision', default_attrs['revision'])
                if default_attrs['remote']:
                    project.setAttribute('remote', default_attrs['remote'])

            remote_attr = project.getAttribute('remote')
            if remote_attr in mirror_site_matrix:
                new_remote = mirror_site_matrix[remote_attr]
                project.setAttribute('remote', new_remote)
        return dom

    def replace_project_path(self, dom):
        manifest = dom.documentElement
        projects = manifest.getElementsByTagName('project')

        for project in projects:
            path_attr = project.getAttribute('path')
            project.setAttribute('path', os.path.join(self.repo_install_path, path_attr))
        return dom
    
    def project_upstream(self, dom):
        manifest = dom.documentElement
        projects = manifest.getElementsByTagName('project')
        for project in projects:
            if project.hasAttribute('upstream'):
                project.removeAttribute('upstream')
            if project.getAttribute('name') == "meta-alb":
                upstream = alb_upstream.get(self.bsp_version)
                if upstream: 
                    project.setAttribute('upstream', upstream)
        return dom


    def process_xml(self):
        dom = self.remove_remote()
        default_attrs = self.extract_default_attributes(dom)
        dom = self.replace_project_remote(dom, default_attrs)
        dom = self.replace_project_path(dom)
        dom = self.project_upstream(dom)

        xml_content = dom.toprettyxml(indent='', newl='')
        xml_content = xml_content.replace('<?xml version="1.0" ?>', "")
        xml_content = xml_content.replace('<manifest>', "")
        output_xml_content = manifest_header.strip() + '\n\n\t' + xml_content.strip()
        output_xml_path = self.xml_output_path

        with open(output_xml_path, 'w', encoding='utf-8') as f:
            f.write(output_xml_content)
        
        print(f"Modified XML saved to {output_xml_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Manifest file to Continental internal mirror site')
    parser.add_argument('--manifest_path', type=str, required=True)
    parser.add_argument('--output_path', type=str, required=True) 
    parser.add_argument('--install_path', type=str, default='')
    parser.add_argument('--bsp_version', type=str)

    args = parser.parse_args()
    converter = ManifestConverter(args.manifest_path, args.output_path, args.install_path,args.bsp_version)
    converter.process_xml()


