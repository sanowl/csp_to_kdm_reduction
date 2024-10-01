from itertools import product, combinations
from collections import defaultdict

# Define the CSP instance
class CSPInstance:
    def __init__(self, R, k, variables, constraints):
        """
        R: Alphabet size
        k: Number of partitions
        variables: List of variables partitioned into k subsets
        constraints: List of constraints, each constraint is a tuple (vars, allowed_assignments)
        """
        self.R = R
        self.k = k
        self.variables = variables  #
        self.constraints = constraints 
        self.variable_partitions = {} 
        
        partition_size = len(variables) // k
        for idx, v in enumerate(variables):
            self.variable_partitions[v] = idx % k  
        
        self.ensure_R_degree_bounded()
    
    def ensure_R_degree_bounded(self):
        variable_constraint_count = defaultdict(int)
        for constraint in self.constraints:
            vars_in_constraint, _ = constraint
            for v in vars_in_constraint:
                variable_constraint_count[v] += 1
        
        for v, count in variable_constraint_count.items():
            if count > self.R:
                raise ValueError(f"Variable {v} appears in {count} constraints, exceeding R={self.R}")
    
    def get_partition(self, variable):
        return self.variable_partitions[variable]

class GadgetGraph:
    def __init__(self, R, variable_name):
        self.R = R
        self.variable_name = variable_name
        self.vertices = [(variable_name, x, y) for x, y in product(range(R), repeat=2)]
        self.edges = defaultdict(list)  # Edges grouped by 'a' value
        self.create_edges()
    
    def create_edges(self):
        for a in range(self.R):
            for b in range(self.R):
                edge = []
                for x in range(self.R):
                    y = (a * x + b) % self.R
                    vertex = (self.variable_name, x, y)
                    edge.append(vertex)
                self.edges[a].append(edge)

class MatchingInstance:
    def __init__(self, k, R):
        self.vertices = set()
        self.edges = []
        self.partitions = defaultdict(set)  
        self.k = k
        self.R = R
    
    def add_vertices(self, vertices, partition_index):
        for vertex in vertices:
            self.vertices.add(vertex)
            self.partitions[partition_index].add(vertex)
    
    def add_edge(self, edge):
        self.edges.append(edge)
    
    def verify_properties(self):
        # Verify k-partite structure
        total_partitions = self.k * self.R
        if len(self.partitions) != total_partitions:
            print(f"Expected {total_partitions} partitions, found {len(self.partitions)}")
            return False
        
        for edge in self.edges:
            partitions_in_edge = set()
            for vertex in edge:
                for partition_idx, partition_vertices in self.partitions.items():
                    if vertex in partition_vertices:
                        partitions_in_edge.add(partition_idx)
                        break
            if len(partitions_in_edge) != len(edge):
                print(f"Edge {edge} does not have vertices from distinct partitions")
                return False
        print("All verification checks passed.")
        return True

# Reduction Function
def reduce_csp_to_matching(csp_instance):
    R = csp_instance.R
    k = csp_instance.k
    variables = csp_instance.variables
    constraints = csp_instance.constraints
    
    gadget_graphs = {}
    for v in variables:
        gadget = GadgetGraph(R, v)
        gadget_graphs[v] = gadget
    
    matching_instance = MatchingInstance(k, R)
    for v in variables:
        gadget = gadget_graphs[v]
        partition_base = csp_instance.get_partition(v) * R
        for a in range(R):
            partition_index = partition_base + a
            vertices_in_partition = set()
            for edge in gadget.edges[a]:
                vertices_in_partition.update(edge)
            matching_instance.add_vertices(vertices_in_partition, partition_index)

    for constraint in constraints:
        vars_in_constraint, allowed_assignments = constraint
        for assignment in allowed_assignments:
            edges_list = []
            for idx, v in enumerate(vars_in_constraint):
                a_i = assignment[idx]
                gadget = gadget_graphs[v]
                edges_with_color_a_i = gadget.edges[a_i]
                edges_list.append(edges_with_color_a_i)
            for edge_combination in product(*edges_list):
                combined_edge = []
                for edge in edge_combination:
                    combined_edge.extend(edge)
                matching_instance.add_edge(combined_edge)
    
    return matching_instance

# Example usage
if __name__ == "__main__":
    R = 3  # Alphabet size
    k = 2  # Number of partitions
    
    U1 = ['v1', 'v2']
    U2 = ['v3', 'v4']
    variables = U1 + U2

    constraints = [
        (['v1', 'v3'], [(0, 1), (1, 2)]), 
        (['v2', 'v4'], [(2, 0), (1, 1)]), 
    ]
    
    csp_instance = CSPInstance(R, k, variables, constraints)
    matching_instance = reduce_csp_to_matching(csp_instance)
    
    # Output the Matching instance
    print("Vertices in the Matching instance:")
    for vertex in matching_instance.vertices:
        print(vertex)
    
    print("\nPartitions:")
    for idx in sorted(matching_instance.partitions.keys()):
        print(f"Partition {idx}: {matching_instance.partitions[idx]}")
    
    print("\nEdges in the Matching instance:")
    for edge in matching_instance.edges:
        print(edge)
    
    # Verification
    print("\nVerification of Matching Instance Properties:")
    matching_instance.verify_properties()
