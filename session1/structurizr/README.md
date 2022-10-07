# Structurizr C4 diagram demo

## How to upload a diagram

1. Create [Structurizr account](https://structurizr.com)
2. Prepare .dsl file with diagram definition
3. Create new Structurizr workspace and get [key/secret credentials](https://structurizr.com/workspace/users)
4. Install [Structurizr client](https://github.com/structurizr/cli/blob/master/docs/getting-started.md)
5. Upload the diagram:
    ```bash
    structurizr-cli push -id WORKSPACE_ID -key KEY -secret SECRET -workspace recommender.dsl
    ```
6. Visit the workspace page to view the diagram
