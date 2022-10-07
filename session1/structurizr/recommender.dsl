workspace "Video Recommender System" "This is an example of the C4 diagram" {

    model {
        creator = person "Admin"
        user = person "Client"

        videoRecommender = softwareSystem "Video Recommender System" "Returns relevant personalized video recommendations" {
            webapp = container "Web Recommender Service" "" "" "Web App" {
                user -> this "Gets recommendations"
            }
            userFeaturizer = container "User Featurizer Model" {
                webapp -> this "Gets user vector"
            }
            knnIndex = container "Videos kNN Index" {
                userFeaturizer -> this "Gets video candidates pool"
            }
            embeddingsUpdaterJob = container "Embeddings Updater Job" "Updates user and video representations and models based on feedback data" {
                this -> knnIndex "Updates videos"
                this -> userFeaturizer "Updates featurizer"
            }
            elastic = container "ElasticSearch" "" "" "Database" {
                knnIndex -> this "Gets ranked videos from the pool"
                this -> webapp "Returns video recommendations"
            }
            bigquery = container "BigQuery" "Storage with user feedback and events" "" "Database" {
                user -> this "Sends feedback"
                embeddingsUpdaterJob -> this "Pulls user feedback"
            }
        }

        videoInjector = softwareSystem "Video Injestion System" {
            cms = container "Content Management System" "" "" "Web App" {
                creator -> this "Uploads a new video"
            }
            queue = container "Queue" {
                cms -> this "Pushes a video"
            }
            injestionJob = container "Injestion Job" {
                captionCreator = component "Captions Generator" "Generates audio captions" {
                    this -> queue "Pulls a video"
                }
                renditionsCreator = component "Renditions Generator" "Generates videos with different resolutions" {
                    captionCreator -> this "Sends a video"
                }
                violationDetector = component "Violation Detector" "Detects potential violations" {
                    renditionsCreator -> this "Sends a video"
                    this -> elastic "Inserts video and metadata"
                }
                this -> elastic "Inserts video and metadata"
            }
        }
    }

    views {
        theme default

        styles {
            element "Web App" {
                shape WebBrowser
            }
            element "Database" {
                shape Cylinder
            }
        }
    }
}
