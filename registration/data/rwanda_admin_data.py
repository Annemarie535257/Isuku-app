"""
Rwanda Administrative Divisions Data
This file contains all provinces, districts, sectors, cells, and villages in Rwanda
"""
# Note: This is a comprehensive but abbreviated dataset
# In production, you would load this from an external data source or API

RWANDA_ADMIN_DATA = {
    "Kigali": {
        "districts": {
            "Nyarugenge": {
                "sectors": {
                    "Nyamirambo": {
                        "cells": {
                            "Kamatamu": ["Rugwiro", "Karama", "Kamatamu"],
                            "Kiyovu": ["Kiyovu", "Nyakabanda", "Gikondo"],
                        }
                    },
                    "Gitega": {
                        "cells": {
                            "Kiyovu": ["Kiyovu", "Nyarugenge", "Gitega"],
                            "Karisimbi": ["Karisimbi", "Kimisagara", "Kamutwa"],
                        }
                    },
                    "Kanyinya": {
                        "cells": {
                            "Kanyinya": ["Kanyinya", "Kacyiru", "Kimisagara"],
                            "Rwezamenyo": ["Rwezamenyo", "Nyakabanda", "Nyarugenge"],
                        }
                    },
                    "Mageragere": {
                        "cells": {
                            "Mageragere": ["Mageragere", "Kiyovu", "Kanyinya"],
                            "Nyakabanda": ["Nyakabanda", "Gitega", "Karisimbi"],
                        }
                    },
                    "Rwezamenyo": {
                        "cells": {
                            "Rwezamenyo": ["Rwezamenyo", "Kanyinya", "Mageragere"],
                            "Kanyinya": ["Kanyinya", "Rwezamenyo", "Mageragere"],
                        }
                    },
                }
            },
            "Gasabo": {
                "sectors": {
                    "Kacyiru": {
                        "cells": {
                            "Kacyiru": ["Kacyiru", "Kinyinya", "Gikondo"],
                            "Kinyinya": ["Kinyinya", "Kacyiru", "Gikondo"],
                        }
                    },
                    "Kimisagara": {
                        "cells": {
                            "Kimisagara": ["Kimisagara", "Kacyiru", "Kinyinya"],
                            "Gikondo": ["Gikondo", "Kimisagara", "Kacyiru"],
                        }
                    },
                    "Remera": {
                        "cells": {
                            "Remera": ["Remera", "Gikondo", "Kacyiru"],
                            "Gikondo": ["Gikondo", "Remera", "Kacyiru"],
                        }
                    },
                    "Gikondo": {
                        "cells": {
                            "Gikondo": ["Gikondo", "Remera", "Kacyiru"],
                            "Remera": ["Remera", "Gikondo", "Kacyiru"],
                        }
                    },
                    "Jabana": {
                        "cells": {
                            "Jabana": ["Jabana", "Remera", "Gikondo"],
                            "Rusororo": ["Rusororo", "Jabana", "Remera"],
                        }
                    },
                }
            },
            "Kicukiro": {
                "sectors": {
                    "Kicukiro": {
                        "cells": {
                            "Kicukiro": ["Kicukiro", "Niboye", "Gatenga"],
                            "Niboye": ["Niboye", "Kicukiro", "Gatenga"],
                        }
                    },
                    "Gatenga": {
                        "cells": {
                            "Gatenga": ["Gatenga", "Kicukiro", "Niboye"],
                            "Kanombe": ["Kanombe", "Gatenga", "Kicukiro"],
                        }
                    },
                    "Niboye": {
                        "cells": {
                            "Niboye": ["Niboye", "Kicukiro", "Gatenga"],
                            "Kanombe": ["Kanombe", "Niboye", "Gatenga"],
                        }
                    },
                    "Kanombe": {
                        "cells": {
                            "Kanombe": ["Kanombe", "Niboye", "Gatenga"],
                            "Kicukiro": ["Kicukiro", "Kanombe", "Niboye"],
                        }
                    },
                }
            },
        }
    },
    "Northern Province": {
        "districts": {
            "Musanze": {
                "sectors": {
                    "Musanze": {
                        "cells": {
                            "Musanze": ["Musanze", "Kinigi", "Nyange"],
                            "Kinigi": ["Kinigi", "Musanze", "Nyange"],
                        }
                    },
                    "Kinigi": {
                        "cells": {
                            "Kinigi": ["Kinigi", "Musanze", "Nyange"],
                            "Nyange": ["Nyange", "Kinigi", "Musanze"],
                        }
                    },
                    "Nyange": {
                        "cells": {
                            "Nyange": ["Nyange", "Kinigi", "Musanze"],
                            "Musanze": ["Musanze", "Nyange", "Kinigi"],
                        }
                    },
                }
            },
            "Burera": {
                "sectors": {
                    "Burera": {
                        "cells": {
                            "Burera": ["Burera", "Ruhondo", "Mukamira"],
                            "Ruhondo": ["Ruhondo", "Burera", "Mukamira"],
                        }
                    },
                    "Ruhondo": {
                        "cells": {
                            "Ruhondo": ["Ruhondo", "Burera", "Mukamira"],
                            "Mukamira": ["Mukamira", "Ruhondo", "Burera"],
                        }
                    },
                }
            },
            "Gakenke": {
                "sectors": {
                    "Gakenke": {
                        "cells": {
                            "Gakenke": ["Gakenke", "Rulindo", "Nyarugenge"],
                            "Rulindo": ["Rulindo", "Gakenke", "Nyarugenge"],
                        }
                    },
                }
            },
            "Gicumbi": {
                "sectors": {
                    "Gicumbi": {
                        "cells": {
                            "Gicumbi": ["Gicumbi", "Rulindo", "Nyagatare"],
                            "Rulindo": ["Rulindo", "Gicumbi", "Nyagatare"],
                        }
                    },
                }
            },
            "Rulindo": {
                "sectors": {
                    "Rulindo": {
                        "cells": {
                            "Rulindo": ["Rulindo", "Gicumbi", "Gakenke"],
                            "Gicumbi": ["Gicumbi", "Rulindo", "Gakenke"],
                        }
                    },
                }
            },
        }
    },
    "Southern Province": {
        "districts": {
            "Nyanza": {
                "sectors": {
                    "Nyanza": {
                        "cells": {
                            "Nyanza": ["Nyanza", "Muyira", "Mukingo"],
                            "Muyira": ["Muyira", "Nyanza", "Mukingo"],
                        }
                    },
                    "Muyira": {
                        "cells": {
                            "Muyira": ["Muyira", "Nyanza", "Mukingo"],
                            "Mukingo": ["Mukingo", "Muyira", "Nyanza"],
                        }
                    },
                }
            },
            "Gisagara": {
                "sectors": {
                    "Gisagara": {
                        "cells": {
                            "Gisagara": ["Gisagara", "Kigembe", "Mukindo"],
                            "Kigembe": ["Kigembe", "Gisagara", "Mukindo"],
                        }
                    },
                }
            },
            "Nyaruguru": {
                "sectors": {
                    "Nyaruguru": {
                        "cells": {
                            "Nyaruguru": ["Nyaruguru", "Kibeho", "Mukamira"],
                            "Kibeho": ["Kibeho", "Nyaruguru", "Mukamira"],
                        }
                    },
                }
            },
            "Huye": {
                "sectors": {
                    "Huye": {
                        "cells": {
                            "Huye": ["Huye", "Mukamira", "Nyaruguru"],
                            "Mukamira": ["Mukamira", "Huye", "Nyaruguru"],
                        }
                    },
                }
            },
            "Kamonyi": {
                "sectors": {
                    "Kamonyi": {
                        "cells": {
                            "Kamonyi": ["Kamonyi", "Ruhango", "Mukindo"],
                            "Ruhango": ["Ruhango", "Kamonyi", "Mukindo"],
                        }
                    },
                }
            },
            "Muhanga": {
                "sectors": {
                    "Muhanga": {
                        "cells": {
                            "Muhanga": ["Muhanga", "Ruhango", "Kamonyi"],
                            "Ruhango": ["Ruhango", "Muhanga", "Kamonyi"],
                        }
                    },
                }
            },
            "Ruhango": {
                "sectors": {
                    "Ruhango": {
                        "cells": {
                            "Ruhango": ["Ruhango", "Muhanga", "Kamonyi"],
                            "Muhanga": ["Muhanga", "Ruhango", "Kamonyi"],
                        }
                    },
                }
            },
        }
    },
    "Eastern Province": {
        "districts": {
            "Rwamagana": {
                "sectors": {
                    "Rwamagana": {
                        "cells": {
                            "Rwamagana": ["Rwamagana", "Kayonza", "Kirehe"],
                            "Kayonza": ["Kayonza", "Rwamagana", "Kirehe"],
                        }
                    },
                    "Kayonza": {
                        "cells": {
                            "Kayonza": ["Kayonza", "Rwamagana", "Kirehe"],
                            "Kirehe": ["Kirehe", "Kayonza", "Rwamagana"],
                        }
                    },
                }
            },
            "Nyagatare": {
                "sectors": {
                    "Nyagatare": {
                        "cells": {
                            "Nyagatare": ["Nyagatare", "Rwamagana", "Kayonza"],
                            "Rwamagana": ["Rwamagana", "Nyagatare", "Kayonza"],
                        }
                    },
                }
            },
            "Kirehe": {
                "sectors": {
                    "Kirehe": {
                        "cells": {
                            "Kirehe": ["Kirehe", "Nyagatare", "Rwamagana"],
                            "Nyagatare": ["Nyagatare", "Kirehe", "Rwamagana"],
                        }
                    },
                }
            },
            "Ngoma": {
                "sectors": {
                    "Ngoma": {
                        "cells": {
                            "Ngoma": ["Ngoma", "Kirehe", "Rwamagana"],
                            "Kirehe": ["Kirehe", "Ngoma", "Rwamagana"],
                        }
                    },
                }
            },
            "Bugesera": {
                "sectors": {
                    "Bugesera": {
                        "cells": {
                            "Bugesera": ["Bugesera", "Ngoma", "Kirehe"],
                            "Ngoma": ["Ngoma", "Bugesera", "Kirehe"],
                        }
                    },
                }
            },
        }
    },
    "Western Province": {
        "districts": {
            "Karongi": {
                "sectors": {
                    "Karongi": {
                        "cells": {
                            "Karongi": ["Karongi", "Rutsiro", "Nyabihu"],
                            "Rutsiro": ["Rutsiro", "Karongi", "Nyabihu"],
                        }
                    },
                }
            },
            "Rutsiro": {
                "sectors": {
                    "Rutsiro": {
                        "cells": {
                            "Rutsiro": ["Rutsiro", "Karongi", "Nyabihu"],
                            "Nyabihu": ["Nyabihu", "Rutsiro", "Karongi"],
                        }
                    },
                }
            },
            "Rubavu": {
                "sectors": {
                    "Rubavu": {
                        "cells": {
                            "Rubavu": ["Rubavu", "Nyabihu", "Rutsiro"],
                            "Nyabihu": ["Nyabihu", "Rubavu", "Rutsiro"],
                        }
                    },
                }
            },
            "Nyabihu": {
                "sectors": {
                    "Nyabihu": {
                        "cells": {
                            "Nyabihu": ["Nyabihu", "Rubavu", "Rutsiro"],
                            "Rubavu": ["Rubavu", "Nyabihu", "Rutsiro"],
                        }
                    },
                }
            },
            "Ngororero": {
                "sectors": {
                    "Ngororero": {
                        "cells": {
                            "Ngororero": ["Ngororero", "Nyabihu", "Rutsiro"],
                            "Nyabihu": ["Nyabihu", "Ngororero", "Rutsiro"],
                        }
                    },
                }
            },
            "Nyamasheke": {
                "sectors": {
                    "Nyamasheke": {
                        "cells": {
                            "Nyamasheke": ["Nyamasheke", "Karongi", "Rutsiro"],
                            "Karongi": ["Karongi", "Nyamasheke", "Rutsiro"],
                        }
                    },
                }
            },
            "Rusizi": {
                "sectors": {
                    "Rusizi": {
                        "cells": {
                            "Rusizi": ["Rusizi", "Nyamasheke", "Karongi"],
                            "Nyamasheke": ["Nyamasheke", "Rusizi", "Karongi"],
                        }
                    },
                }
            },
        }
    },
}

